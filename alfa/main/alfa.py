#!/bin/python3
import os
from .analyser import Analyser
from .activity import Activities, Activity
from .event import Events
from pandas.core.series import Series
from pandas import to_datetime
from typing import Tuple, Union
from functools import reduce

from ..config import config
from .kill_chain import KillChain
from .collector import Collector

class Alfa:
    '''Takes all suspicious activities and creates a separate "events"
        attribute that holds all events.
    Each event contains a reference to its corresponding activity.

    Can be initialized as empty, or with an Activities dataframe.
    Typically will be initialized through static methods:
        Alfa.load, Alfa.load_unfiltered, or Alfa.query
    '''
    activities = Activities(**config['activity_defaults'])
    events = Events()

    def __init__(self, activity_list: list = None) -> None:
        self.collector = Collector()
        if activity_list is not None:
            self.activities = Activities(activity_list)
            self.events = self.initialize_events()
            self.activities = self.activities.fillna('')
        pass

    def __get_events(self, activity: Series) -> list:
        return activity['events']

    def __get_all_events(self) -> Tuple[list, list]:
        all_events = []
        if self.activities.shape[0] == 0:
            return []
        for activity in self.activities.iloc:
            activity_id = activity.name
            new_events = self.__get_events(activity)
            for event in new_events:
                event['activity_id'] = activity_id
                event['activity_time'] = to_datetime(activity['id.time'])
            all_events = all_events + new_events

        return all_events

    def __create_events(self, all_events: list) -> Events:
        E = Events(all_events)
        if 'activity_time' not in E:
            print('warning: no data in dataset!')
            E.parent = self
            return E
        # throws an error if dataframe is empty
        E = E.sort_values('activity_time', ignore_index=True)
        E.parent = self
        return E

    def initialize_events(self) -> Events:
        all_events = self.__get_all_events()
        return self.__create_events(all_events)

    def activity_by_id(self, uid: str) -> Activity:
        return self.activities.loc[uid]

    def filter(self, filter_array: Series) -> 'Alfa':
        '''
    Filters on *activities* and returns a new Alfa object.
    Input should be slice of an Activites dataframe.
    e.g. A.activities[A.activities['actor.email'].str.startswith('attacker')]
    will return activities whose email starts with 'attacker'
        '''
        filtered_activities = self.activities[filter_array]
        return Alfa(filtered_activities)

    def kcs(self, start_index: int = 0, end_index: int = None):
        '''
        return a kill_chain_statistic for the entire set of events,
        if called with no params, else acts on a slice.
        '''
        E = self.events['attack.index']
        if end_index and end_index > start_index:
            E = E.iloc[slice(start_index, end_index)]
        return KillChain.generate_kill_chain_statistic(list(E))

    def subchains(self, min_length=None, min_stat=None):
        subchains = KillChain.discern_subchains(
            self.events['attack.index'], min_length, min_stat)
        return sorted(subchains, key=lambda x: x[2], reverse=True)

    @staticmethod
    def acquire(logtype: str, *args, **kwargs) -> Union[list, dict]:
        '''
        Collect records from API, do not process them
        This is a wrapper around Collector, see Collector.query for for details
        '''
        C = Collector()
        res = C.query(logtype, *args, **kwargs)  # this return a dataframe
        return res

    @staticmethod
    def query(logtype: str, filter=True, *args, **kwargs):
        '''
        Query API directly, returns an Alfa object. See collector
        '''
        C = Collector()
        A = Analyser()
        Q = C.query(logtype, *args, **kwargs)
        records = A.analyse(Q, filter=filter)
        return Alfa(Activities(records))

    @staticmethod
    def load(logtype: str, path: str = None, email: list = None, filter: bool = True) -> None:
        '''
        load a log (or all logs), the data/ folder label and *filter* and
        return an Alfa object. Optionally filter by email.
        See analyser for details
        '''
        A = Analyser()
        C = Collector()
        if logtype == 'all':
            all_ = C.load_all(path)
            records = A.analyse(all_, email=None, filter=filter)
            return Alfa(Activities(records))
        Q = C.load(os.path.join(path, logtype+'.json'))
        records = A.analyse(Q, email=None, filter=filter)
        return Alfa(Activities(records))

    def __aoi(self, concat: bool = True):
        '''
        Activities of Interest
        Automates the following:
            1. get subchains
            2. join subchains that are close by
            3. grab event slices from those subchains
            4. list out the unique activities associated with those subchains
        concat: bool, if True (default) then append
                the activity slices to one another
        '''
        subchains = self.subchains()
        long_chains = KillChain.join_subchains_loop(subchains)
        event_slices = self.events.get_event_slices(long_chains)
        activity_slices = [e.activities() for e in event_slices]
        if len(activity_slices) == 0: # prevent possible concat on empty list
            return activity_slices
        if concat:
            res = reduce(lambda a, b: a.append(b), activity_slices)
            res = res[~res.index.duplicated()]
            return res
        return activity_slices

    def aoi(self, export: str = None, nd: bool=False):
        '''
        wrapper around __aoi (above)
        adds the export functionality
        exports as an array of records [ {...}, {...}, ...]
        '''
        aoi = self.__aoi()
        if export is not None:
            if nd:
                with open(export, 'w') as f:
                    for _, row in aoi.iterrows():
                        f.write(row.to_json()+'\n')
            else:
                aoi.to_json(export, orient='records')
            print('saved to', export)
        return aoi
