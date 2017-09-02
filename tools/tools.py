"""
* author: Gavin Hull
* version: 2017.08.22
* description: Tools to manipulate data from JSON reports
"""

from __future__ import print_function
import datetime
from printer import Printer


class Tools(object):

    def __init__(self):
        self.printer = Printer(True)

    # Convert the time into human readable format
    def time_convert(self, t_time):
        return datetime.datetime.fromtimestamp(t_time)

    # Get the difference in time and return a string of it converted
    def time_diff(self, t_from, t_to):
        t_diff = t_to - t_from
        time_diff = ""
        # if t_diff < 0:
        #     t_diff = t_from - t_to
        try:
            if abs(t_diff) >= 3600:
                time_diff = self.time_convert(t_diff).strftime('%H:%M:%S.%f')
            elif abs(t_diff) >= 60:
                time_diff = self.time_convert(t_diff).strftime('%M:%S.%f')
            elif abs(t_diff) >= 0:
                time_diff = self.time_convert(t_diff).strftime('%S.%f')
            else:
                time_diff = self.time_convert(t_diff).strftime('0.%f')
        except ValueError as err:
            self.printer.print_error("Time is wrong value from %s to %s. %s" % (t_from, t_to, err))

        return time_diff

    def time_diff_s(self, t_from, t_to):
        return t_to - t_from
