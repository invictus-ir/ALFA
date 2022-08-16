from pandas.core.series import Series
from pandas.core.frame import DataFrame


class Activity(Series):
    '''
    A dataframe containing activities
    '''
    @property
    def _constructor(self):
        return Activity

    @property
    def _constructor_expanddim(self):
        return Activities

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def convert(series: Series) -> 'Activity':
        return Activity(series._data)


class Activities(DataFrame):
    @property
    def _constructor(self):
      return Activities

    @property
    def _constructor_sliced(self):
      return Activity

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if 'id.uniqueQualifier' in self.columns:
            self.set_index('id.uniqueQualifier',inplace=True)
