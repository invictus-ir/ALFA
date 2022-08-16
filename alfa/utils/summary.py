from tabulate import tabulate
from ..main.event import Events
from ..main.activity import Activities

event_columns = ['name','activity_time','activity_id']

activity_columns = ['id.time','kind','actor.email','id.applicationName']

def summary(data):
    '''
        wraps around tabulate
        prints a summary of data in a tabled format
    '''
    if type(data) == Events:
        print(tabulate(data[event_columns],headers=event_columns))
    elif type(data) == Activities:
        print(tabulate(data[activity_columns],headers=activity_columns))
    else:
        print(tabulate(data))

