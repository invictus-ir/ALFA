#!/bin/python3

from pandas import isna
from ..config import config
kc_conf = config['kill_chain']


class KillChain:
    '''
    KillChain takes a list of events and assigns a value from chain_dict, based on the even't category.
    The KillChain Statistic is a value, from -1 to 1, that indicates how well the traditional kill-chain attack is followed.

    -1 indicates that the kill_chain was followed in reverse. 0 is totally random. 1 indicates a 100% follow-through.
    '''

    reductive_methods = {
        'mean': lambda x: sum(x)/len(x),
        'min': min,
        'max': max
    }

    chain_dict = {
        "persistence": 1,
        "privilege_escalation": 2,
        "defense_evasion": 3,
        "credential_access": 4,
        "discovery": 5,
        "lateral_movement": 6,
        "collection": 7
    }

    @staticmethod
    def generate_kill_chain_statistic(chain_index_list: list) -> float:
        '''
          Input: list of attack_indexes
          Output: statistic

          sum -> 0, count-> 0
          For each index:
            if prev_index < index:
              sum += 1, count +=1
            if prev_index > index:
              sum -= 1, count += 1

          Output -> sum / count
        '''
        result = 0
        chain_size = len(chain_index_list)
        total_unique_indexes = 0
        prev_value = chain_index_list[0]
        for i in range(1, chain_size):
            if isna(chain_index_list[i]):
                continue
            if chain_index_list[i] > prev_value:
                result += 1
                total_unique_indexes += 1
                prev_value = chain_index_list[i]

            elif chain_index_list[i] < prev_value:
                result -= 1
                total_unique_indexes += 1
                prev_value = chain_index_list[i]
            elif chain_index_list[i] == prev_value:
                result -= 1/len(chain_index_list) # decrement result slowly if previous value is the same as current value
        if total_unique_indexes == 0:
            return 0
        return result / total_unique_indexes

    @staticmethod
    def assign_index(category):
        return KillChain.chain_dict[category]

    @staticmethod
    def reduce_category_list(category_list):
        '''
        Used to reduce attack indexes to a single value. It takes the categories (tactics) and maps them according to KillChain.chain_dict
        Then it uses the chosen reductive method (in config.yml), to reduce the value to a single number. Reductive methods available:
        mean, min, & max.
        '''
        category_as_indexes = [
            KillChain.assign_index(c) for c in category_list]
        return KillChain.reductive_methods[kc_conf['index_reducer']](category_as_indexes)

    @staticmethod
    def __discern_single_subchain(chain_index_list: list, start_index: int, min_length: int, min_stat: float, max_slack_width: int=kc_conf['max_slack_width'], max_slack_depth: int= kc_conf['max_slack_depth']) -> list:
        '''
        Output: [start_index, end_index, statistic]

        growing phase: Not shrinking phase
        while True
          growing phase:
            if better (or equal) stats:
              set candidate
              grow (end_index += 1)
              repeat
            else:
              set phase to shrinking

          if shrinking:
            shrink (start_index += 1)
            if better stats:
              set candidate
              if too small:
                end
            if run out of tries (max_shrink_no_change):
              end
            repeat

          check statistic for slice between start_index, end_index
          if slice better than prev_slice, set it as candidate
            if growing:
              increase end_index by 1
            if shrinking:
              increase start_index by 1

        start by growing, and change to shrinking when:
          end_index is length of chain
          stat no longer increases

        End loop when:
          in shrinking phase and:
            stat no longer increasing
            length of slice is min_length
      '''
        end_index = min(start_index + min_length, len(chain_index_list))

        prev_stat = 0
        candidate = None

        shrinking_phase = False
        max_shrink_no_change = min_length
        shrink_amount = 0
        slack_width = 0

        while True:
            if shrinking_phase:
                shrink_amount += 1
            SI = start_index + shrink_amount
            subchain = chain_index_list[SI:end_index]
            stat = KillChain.generate_kill_chain_statistic(subchain)

            if stat > min_stat:
                if not shrinking_phase:  # First phase "Growing" phase
                    SI = start_index
                    # Greedy. Greater than OR equal to. Try and grow as much as possible.
                    if stat >= prev_stat:
                        candidate = [SI, end_index, stat]
                        prev_stat = stat
                        end_index += 1
                        slack_width = 0
                        if end_index >= len(chain_index_list):
                            shrinking_phase = True
                            end_index = len(chain_index_list)
                        continue
                    elif slack_width < max_slack_width:
                        final_index = chain_index_list[end_index-1]
                        index_before_slack = chain_index_list[end_index - (2+slack_width)]
                        if index_before_slack - final_index < max_slack_depth:
                            slack_width += 1
                        else:
                            shrinking_phase = True
                            slack_width = 0
                            end_index -= 1
                    else:
                        shrinking_phase = True
                        slack_width = 0
                        end_index -= 1+slack_width
                        continue

                elif shrinking_phase:  # Second phase
                    if stat > prev_stat:  # Lazy. Shrink as little as possible. Shrink ONLY IF GREATER THAN
                        candidate = [SI, end_index, stat]
                        prev_stat = stat
                        if (end_index - start_index <= min_length):  # shrunk too small
                            break
                    elif shrink_amount < max_shrink_no_change:  # still opportunity to shrink
                        continue
            break
        return candidate
    

    @staticmethod
    def join_close_subchains(subchain_list: list, min_chain_length: int = kc_conf['min_chain_length']) -> list:
        subchain_list.sort(key=lambda x: x[0])
        i = len(subchain_list) - 1
        new_chains = []
        change_count = 0
        while i >= 0:
            if i == 0:
                new_chains.insert(0, subchain_list[0][:2])
                break

            curr_chain = subchain_list[i]
            prev_chain = subchain_list[i-1]
            if curr_chain[0] - prev_chain[1] < min_chain_length:
                new_chains.insert(0,[prev_chain[0], curr_chain[1]])
                i -= 2
                change_count += 1
            else:
                new_chains.insert(0,curr_chain[:2])
                i -= 1
        return new_chains, change_count

    @staticmethod
    def join_subchains_loop(chain_index_list: list, min_chain_length: int = kc_conf['min_chain_length']) -> list:
        jsc, count = KillChain.join_close_subchains(
            chain_index_list, min_chain_length)
        while count:
            jsc, count = KillChain.join_close_subchains(jsc, min_chain_length)
        return jsc

    @staticmethod
    def discern_subchains(chain_index_list: list, min_length: int = None, min_stat: int = None) -> list:
        '''
        Takes in a list of attack_indexes, outputs subchains within it. Output in the form -> [ [start_index, end_index, statistic], ...]
        Discover subchains within a series. Uses the configs in the config.yaml file if not defined:
          - min_chain_length
          - min_chain_statistic
        '''
        if min_length == None:
            min_length = kc_conf['min_chain_length']
        if min_stat == None:
            min_stat = kc_conf['min_chain_statistic']

        chain_index_list = list(chain_index_list)
        subchains = []
        start_index = 0
        while start_index < (len(chain_index_list) - min_length):
            candidate = KillChain.__discern_single_subchain(
                chain_index_list, start_index, min_length, min_stat)
            if candidate:
                subchains.append(candidate)
                start_index = candidate[1]  # end_index
            else:
                start_index += 1
        return subchains
