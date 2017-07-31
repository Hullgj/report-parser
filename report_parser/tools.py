from __future__ import print_function
import datetime


class Tools(object):

    def __init__(self):
        pass

    # Convert the time into human readable format
    @staticmethod
    def time_convert(t_time):
        return datetime.datetime.fromtimestamp(t_time)

    # Get the difference in time and return a string of it converted
    def time_diff(self, t_from, t_to):
        t_diff = t_to - t_from
        if abs(t_diff) >= 3600:
            t_diff = self.time_convert(t_diff).strftime('%H:%M:%S.%f')
        elif abs(t_diff) >= 60:
            t_diff = self.time_convert(t_diff).strftime('%M:%S.%f')
        elif abs(t_diff) >= 0:
            t_diff = self.time_convert(t_diff).strftime('%S.%f')
        else:
            t_diff = self.time_convert(t_diff).strftime('0.%f')

        return t_diff
