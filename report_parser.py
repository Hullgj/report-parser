from __future__ import print_function

import sys
import argparse
import json
import datetime
from os import walk

from os import print

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


class Parse(object):

    def __init__(self, printer):
        self.printer = printer
        self.tools = Tools()

    # get a list of APIs used by tracked processes and their execution times
    # any duplicate api names have the process end flag 'p_end' appended and only the last
    # one is stored in the dictionary. This then gives the start and end times of when
    # the process was called. We sort the api_dict by value, which is time before storing in the
    # process_list
    # DEV: might need to count the number of times the process was called
    @staticmethod
    def get_tracked_process(json_data, condition):
        process_list = []
        for process in json_data['behavior']['processes']:
            if process['track'] == condition:
                api_dict = {process['process_name']: process['first_seen']}
                for call in process['calls']:
                    if call['api'] not in api_dict:
                        api_dict[call['api']] = call['time']
                    else:
                        api_dict[call['api'] + ' - p_end'] = call['time']

                # api_dict = sorted(api_dict.items(), key=operator.itemgetter(1))
                process_list.append(api_dict)

        return process_list

    def parse_data(self, j_data, output_file):
        self.printer.line_comment("General Information")

        j_analysis_started = j_data['info']['started']
        j_analysis_ended = j_data['info']['ended']

        self.printer.write_file(output_file, "Analysis duration: %s" %
                                self.tools.time_diff(j_analysis_started, j_analysis_ended))

        self.printer.line_comment("Process Behaviour")

        j_generic = j_data['behavior']['generic']

        self.printer.write_file(output_file, "Binary injected: %s after %s" % (
            j_generic[0]['process_name'], self.tools.time_diff(j_analysis_started, j_generic[0]['first_seen'])))
        # write_file(output_file, "Process loaded: %s after %s" % (j_generic[1]['process_name'],
        #     time_diff(j_analysis_started, j_generic[1]['first_seen'])))

        tracked_dict = self.get_tracked_process(j_data, True)
        self.printer.write_file(output_file, "Tracked processes: %s" %
                                json.dumps(tracked_dict, sort_keys=True, indent=4))

    def parse_files(self, p_dir, output_file):
        # loop over files in a directory,
        # ref: https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
        for (dir_path, dir_names, file_names) in walk(p_dir):
            for name in file_names:
                j_comment = "Read and parse from json file: " + name
                self.printer.line_comment(j_comment)
                # open json data and load it
                self.printer.dev_comment("Might need to check if the file is type JSON")
                with open(dir_path + name) as json_file:
                    j_data = json.load(json_file)

                self.parse_data(j_data, output_file)


def main():
    parser = argparse.ArgumentParser(description="process all JSON files in the given directory"
                                                 "outputting the results in the given filename")
    parser.add_argument("parse_dir", help="enter the directory to parse")
    parser.add_argument("output_file", help="enter the file where the results will be written")
    parser.add_argument("-v", "--verbose", action="store_true", help="set verbose output")
    args = parser.parse_args()

    if args.verbose:
        printer = Print(True)
    else:
        printer = Print(False)

    p_dir = args.parse_dir
    output_file = args.output_file

    printer.standard_output('Chosen directory %s. Wait for file: %s to be generated' % (p_dir, output_file))
    printer.standard_output('verbose is set to: %r' % printer.get_verbose())

    printer.write_file(output_file, '', 'w')

    parser = Parse(printer)
    parser.parse_files(p_dir, output_file)


if __name__ == "__main__":
    sys.exit(main())
