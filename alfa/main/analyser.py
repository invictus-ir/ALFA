#!/bin/python3
import yaml
import pandas as pd

from ..utils.path import rel_path, CONFIG_DIR, DATA_DIR
from ..config import config
from .kill_chain import KillChain

class Analyser:
  '''
  uses /config/event_to_mitre.yml to map events in the log to the mitre attack framework.

  analyse... takes a df_name (e.g. login) as input and returns a dataframe of all suspicious records. These are records where
  at least 1 event exists within the event_to_mitre yml database.

  Each event for each record is given new attributes 'attack.label' 'attack.category' and 'attack.index' for all associated mitre attacks for that event.
  '''
  def __init__(self) -> None:
      self.event_mapping = yaml.safe_load(open(rel_path(CONFIG_DIR,'event_to_mitre.yml')))
  
  def analyse_all_files(self, email: list=None,filter=True, subdir=None) -> pd.DataFrame:
    '''Takes all files, analyses and concats into a single DataFrame'''
    df = pd.DataFrame()
    for log in config['logs']:
      log_df = self.analyse_from_file(log,email,filter=filter, subdir=subdir)
      df = df.append(log_df)
    return df
  def analyse_all(self,log_dict,email: list=None,filter=True) -> pd.DataFrame:
    '''takes dict of logs, and analyses and concats them into a single DataFrame'''
    df = pd.DataFrame()
    for log in log_dict:
      log_df = self.analyse(log_dict[log],email,filter=filter)
      df = df.append(log_df)
    return df
    
  def load_file(self,logtype,subdir=None):
    '''Loads file from data/ directory. If a subdir is given, will load from data/<subdir>'''
    df_name = logtype+'.pkl'
    if subdir:
      filename = rel_path(DATA_DIR,subdir,df_name)
    else:
      filename = rel_path(DATA_DIR,df_name)
    return pd.read_pickle(filename)
  
  def analyse_from_file(self,logtype: str,email=None,filter=True, subdir=None):
    '''load file and pass to analyse method'''
    df = self.load_file(logtype, subdir=subdir)
    return self.analyse(df,email,filter=filter)
  
  def label_row(self,row: pd.Series,email: list=None) -> pd.DataFrame:
    '''labels given row from config/event_to_mitre.yml. If email is passed, will filter on those email/s'''
    has_labels = False
    if email:
      if 'actor.email' not in row:
        return None, has_labels
      if row['actor.email'] not in email:
        return None, has_labels
    for event in row['events']:
      if event['name'] in self.event_mapping:
        has_labels = True
        attack_label = self.event_mapping[event['name']]
        attack_category = [label.split('.')[-1] for label in attack_label]
        event['attack.label'] = attack_label
        event['attack.category'] = attack_category
        event['attack.index'] = KillChain.reduce_category_list(attack_category)
    return row, has_labels

  def analyse(self,df: pd.DataFrame,email: list=None, filter: bool=True) -> pd.DataFrame:
    '''takes a DataFrame, outputs labelled, *filtered, DataFrame. Filter will filter out benign events. If email is passed, will only contain events from that email address.'''
    mitre_df = []
    for row in df.iloc:
      row, add_row = self.label_row(row,email)
      if (filter and add_row) or not filter:
        mitre_df.append(row)
    return pd.DataFrame(mitre_df)
