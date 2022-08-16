#!/bin/python3

def event_to_mitre(root: str,_obj: object,event_dict: dict) -> dict:

  '''
  This is typically run as a standalone file, alongside mappings.yml.
  Takes the mitre mappings.yml file and inverts it,
  such that events map to attacks. event => attack.category. this is saved to config/event_to_mitre.yml

  event_to_mitre takes a root string (initialized as ''), an object to remap, and the event dictionary. It outputs the event dictionary, filled.

  if _obj is a list, then it must be a list of events
  for each event:
    if the event is not in the dictionary, initialize as empty list []
    append the root to the dictionary
  
  if _obj is NOT a list, then it must be a dictionary
  for each key in the dictionary, prepend the key to the root:
      new_root = key + '.' + old_root
  then perform recursion, calling event_to_mitre with
  new_root, _obj[key] as _obj and the event_dict

  This is a recursive operation.
  '''
 
  if type(_obj) == list:
    for event in _obj:
      if not event in event_dict:
        event_dict[event] = []
      event_dict[event].append(root[:-1])
    return event_dict

  for key in _obj:
    event_to_mitre(f'{key}.{root}',_obj[key],event_dict)
  return event_dict


if __name__ == '__main__':
  import yaml
  from utils.path import *

  input_file = rel_path(UTILS_DIR,'mappings.yml')
  output_file = rel_path(CONFIG_DIR,'event_to_mitre.yml')

  mappings = yaml.safe_load(open(input_file))
  event_dict = dict()
  event_to_mitre('',mappings,event_dict)

  with open(output_file,'w') as f:
    yaml.safe_dump(event_dict,f)
  
  print('saved to', output_file)