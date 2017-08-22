"""
* author: Gavin Hull
* version: 2017.08.22
* description: This class contains print functions that outputs information to the command prompt, writes data to files, and opens
files as a JSON object
"""

from __future__ import print_function
import os.path
import json


class Printer(object):

    def __init__(self, verbose):
        self.verbose = verbose

    def set_verbose(self, condition):
        self.verbose = condition

    def get_verbose(self):
        return self.verbose

    def print_error(self, error_line):
        if self.verbose:
            print('[ERROR' + 5 * '!' + ']' + error_line)

    # make a comment that takes up a whole line
    def line_comment(self, msg):
        if self.verbose:
            print(5 * '-' + 2 * '+' + ' ' + msg + ' ' + 2 * '+' + 5 * '-')

    @staticmethod
    def standard_output(msg):
        print(msg)

    # make a comment for developers
    def dev_comment(self, msg):
        if self.verbose:
            print("[DEV COMMENT]: " + msg + 10 * '.')

    # write the line to a file, truncating the file if supplied with option 'w' otherwise defaults to 'a' for append
    @staticmethod
    def write_file(output_file, line, mode='a'):
        with open(output_file, mode) as output_file:
            if mode == 'w':
                output_file.truncate()
            print(line, file=output_file)

    def open_json(self, in_file, obj_list=''):
        """Open a file and check it is a JSON file, returning the JSON data"""
        if not os.path.isfile(in_file):
            Print.write_file(in_file, '', 'w')

        with open(in_file, 'r') as json_file:
            if os.path.getsize(in_file) < 8:
                obj_json = {}
                for obj in obj_list:
                    self.line_comment("Adding Object " + obj + " to " + in_file)
                    obj_json[obj] = {}

                Print.write_file(in_file, json.dumps(obj_json, sort_keys=True, indent=4))

            json_data = json.load(json_file)

        return json_data
