#!/bin/python3
'''
holds the parser configuration for the command line
'''
from argparse import ArgumentParser
from .project_creator import Project
from .main import *
from IPython import embed
import os.path, yaml

from pprint import pprint
from tabulate import tabulate

banner = '''
use 'A' to access the Alfa object. A? for more info
'''

class Parser:
    def __init__(self):
        self.parser = ArgumentParser()
        self.subparsers = self.parser.add_subparsers(title='subcommands',required=True,dest='subcommand',
                metavar='init, acquire, analyze, load')
        self.parser_init = self.subparsers.add_parser('init',
                help='intialize a project directory')
        self.parser_acquire = self.subparsers.add_parser('acquire',aliases=['a','ac'],
                help='acquire audit log data and save to the data/ directory')
        self.parser_analyze = self.subparsers.add_parser('analyze',aliases=['aa','an'],
                help='acquire and analyze audit log data, dropping into an interactive shell')
        self.parser_load = self.subparsers.add_parser('load',aliases=['l'],
                help='load offline data, analyze and drop into a shell')

        self.add_init_args()
        self.add_load_args()
        self.add_default_args(self.parser_acquire)
        self.add_default_args(self.parser_analyze)
        self.add_analyze_args()

        self.parser_init.set_defaults(func=self.handle_init)
        self.parser_acquire.set_defaults(func=self.handle_acquire)
        self.parser_analyze.set_defaults(func=self.handle_analyze)
        self.parser_load.set_defaults(func=self.handle_load)

    def add_init_args(self):
        self.parser_init.add_argument('path',type=str,
                help='path to project directory')
        pass

    def add_load_args(self):
        self.parser_load.add_argument('-l','--logtype',type=str,default='all',
                help='log type to load e.g. "drive"')
        self.parser_load.add_argument('-p','--path', type=str, required=True,
                help='directory to load, e.g. --path data/foo')
        pass

    def add_analyze_args(self):
        self.parser_analyze.add_argument('-s','--save',action='store_true',
                help='save data to data/ to load later')
        pass

    def add_default_args(self, subparser):
        subparser.add_argument('-l','--logtype',type=str,default='all',
                help='log type to load e.g. "drive"')
        subparser.add_argument('-p','--path',type=str,
                help='save under path e.g. --path data/foobar')
        subparser.add_argument('--user', required=False, type=str, default='all')
        subparser.add_argument('--no-filter', required=False, action='store_false', dest='filter',
                help='disable filtering of benign activities from dataset')
        subparser.add_argument('--max-results',type=int,required=False,default=1000,
                help='max results per page. max value = 1000 (default)')
        subparser.add_argument('--max-pages',type=int,required=False,default=None,
                help='max number of pages to collect (default = as many as possible)')
        subparser.add_argument('-st','--start-time',type=str,required=False,default=None,
                help='start collecting from date (RFC3339 format)')
        subparser.add_argument('-et','--end-time',type=str,required=False,default=None,
                help='collect until date (RFC3339 format)')
        subparser.add_argument('-q','--query',type=str,
                help='supply a yaml file containing query information. e.g. logtype, save path etc.')
        subparser.add_argument('--nd',action='store_true',help='save data as newline delimited')

    def handle_init(self, args):
        project = Project(args.path)
        print('now run "alfa analyze"!')
        pass

    def handle_load(self, args):
        A = Alfa.load(args.logtype, path=args.path)
        # code.interact(banner=banner,local=locals())
        print(banner)
        embed(display_banner=False)
        pass

    def handle_acquire(self, args):
        if args.query:
            query = self.load_query(args.query)
            query['save'] = True
            A = Alfa.acquire(**query)
        else:
            query = vars(args)
            query['save'] = True
            A = Alfa.acquire(**query)
        # should interactivity be a thing for acquiring?
        # code.interact(banner=banner, local=locals())
        pass

    def handle_analyze(self, args):
        if args.query:
            query = self.load_query(args.query)
            A = Alfa.query(**query)
        else:
            A = Alfa.query(**vars(args))
        print(banner)
        embed(display_banner=False)
        pass

    def load_query(self,filename: str) -> dict:
      if not os.path.exists(filename):
        print('cannot find file:',filename)
        return dict()
      with open(filename) as f:
        query = yaml.safe_load(f)
      return query

    def do_summary(self,A: Alfa):
        print('\n\n---------- Events ---------------\n\n')
        pprint(A.events[['type','attack.category']].head())
        print('\n\n')
        print('num_events:',A.events.shape[0])
        print('num_activities:',A.activities.shape[0])
        print('\n--------------------------------------\n\n')
        print('\n---------- Kill Chains ---------------\n\n')
        print('kill chain statistic: ', A.kcs())
        print('subchains discovered: ')
        print(tabulate(A.subchains(),headers=['start','end','kcs'],tablefmt='fancy_grid'))
        print('\n--------------------------------------\n\n')
        pass
