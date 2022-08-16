from pandas.core.series import Series
from pandas.core.frame import DataFrame
from .activity import Activity


class Events(DataFrame):
    '''
    Events is a dataframe containing events. It has a custom property: parent, which references its Mitre parent.

    Each Event *class* is dynamically generated from the current Events instance. This is because each instance of the class needs a reference
    to its parent (Events).

    Each event's Activity can be accessed through the .activity accessor. e.g. events.iloc[0].activity => Activity.
    This is done by calling the Mitre.activity_by_id method.

    When accessing an event's activity, the event passes the activity id up the chain, and then the mitre object passes it down:

    event /> Events /> Mitre \> activities \> activity 
    '''
    @property
    def _constructor(self):
        return Events

    @property
    def _constructor_sliced(self):
        return EventConstructor(self)

    _metadata = ['parent']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def activity(self, uid: str) -> Activity:
        return self.parent.activity_by_id(uid)

    def activities(self):
        ids = self['activity_id'].unique()
        activities = self.parent.activities.loc[ids] # for some reason returns duplicate rows
        return activities[~activities.index.duplicated()]


    def get_event_slices(self, slices: list):
        '''
            slices: list of iterables with an internal shape of at least 2
                    only the first 2 items in the internal shape are regarded.
                    e.g [ [0,5], [7,22], ...]
            returns a list of slices from the events dataframe
        '''
        out = []
        for item in slices:
            assert len(item) > 1
            s = slice(item[0], item[1])
            out.append(self[s])
        return out

def EventConstructor(parent=None):
    class Event(Series):
        @property
        def _constructor(self):
            return Event

        @property
        def _constructor_expanddim(self):
            return Events
        _metadata = ['name', 'parent', 'activity_id']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.parent = parent

        @property
        def activity(self):
            return self.parent.activity(self['activity_id'])

    return Event
