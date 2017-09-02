"""
* author: Gavin Hull
* version: 2017.08.22
* description: This reads JSON data from all files in a given directory, where the files are Cuckoo Sandbox reports.
The data is then parsed to get the tracked data, including API calls, signatures and their relevant data. This
effectively collects data and hence reduces the search space for every Cuckoo report.
"""

import json
from os import walk

from tools.tools import Tools


class Parser(object):

    def __init__(self, printer):
        self.printer = printer
        self.tools = Tools()
        self.process_list = []

    def map_signatures(self, json_data):
        """Parse the signatures in the JSON file, mapping each to a state in the probabilistic model"""
        api_dict = {}

        for signature in json_data['signatures']:
            set_call = False
            set_category = False
            set_entropy = False
            set_other = False
            api_dict[signature['name']] = {'description': signature['description']}  # initial assignment
            this_api_dict = api_dict[signature['name']]
            this_api_dict['detections'] = signature['markcount']

            for j, mark in enumerate(signature['marks']):
                if 'call' in mark:
                    this_api_dict['api'] = mark['call']['api']
                    this_api_dict['category'] = mark['call']['category']

                    if not set_call:
                        this_api_dict['indicators'] = {'timestamps': [mark['call']['time']]}
                        this_api_dict['called_first'] = mark['call']['time']
                        set_call = True
                    else:
                        this_api_dict['indicators']['timestamps'].append(mark['call']['time'])
                        this_api_dict['called_last'] = mark['call']['time']

                    if 'arguments' in mark['call']:
                        this_api_dict['indicators']['arguments'] = mark['call']['arguments']

                elif 'category' in mark:
                    this_api_dict['category'] = mark['category']

                    if not set_category:
                        this_api_dict['indicators'] = {'ioc': [mark['ioc']]}
                        set_category = True
                    else:
                        this_api_dict['indicators']['ioc'].append(mark['ioc'])

                elif 'entropy' in mark:
                    this_api_dict['category'] = "cryptography"

                    if not set_entropy:
                        this_api_dict['indicators'] = {'entropy': [mark['entropy']],
                                                       'description': [mark['description']]}
                        set_entropy = True
                    else:
                        this_api_dict['indicators']['description'].append(mark['description'])
                        this_api_dict['indicators']['entropy'].append(mark['entropy'])
                elif 'description' in mark:
                    if not set_other:
                        this_api_dict['indicators'] = {'other': [mark['description']]}
                        set_other = True
                    else:
                        this_api_dict['indicators']['other'].append(mark['description'])

            api_dict[signature['name']] = this_api_dict

        return api_dict

    @staticmethod
    def get_tracked_process(json_data, condition):
        """get a list of APIs used by tracked processes and their execution times any duplicate api names have the
        process end flag 'p_end' appended and only the last one is stored in the dictionary. This then gives the start
        and end times of when the process was called. We sort the api_dict by value, which is time before storing in the
        process_list.
        Returns a dictionary of all the processes and their first/last times, the first/last time of the sample, and the
        name"""
        api_dict = {}
        seen_first = 0
        seen_last = 0

        for process in json_data['behavior']['processes']:
            # if json_data['target']['file']['name'] == process['process_name']:
            if process['track'] == condition:
                seen_first_tmp = process['first_seen']
                if seen_first == 0:
                    seen_first = seen_first_tmp
                elif seen_first > seen_first_tmp:
                    seen_first = seen_first_tmp
                for call in process['calls']:
                    if call['api'] not in api_dict:
                        api_dict[call['api']] = {'timestamps': [call['time']]}
                        api_dict[call['api']]['count'] = 1
                    else:
                        api_dict[call['api']]['timestamps'].append(call['time'])
                        api_dict[call['api']]['count'] += 1

                    if seen_last < call['time']:
                        seen_last = call['time']
                    if seen_first > call['time']:
                        seen_first = call['time']

        return seen_first, seen_last, api_dict

    def parse_data(self, name, j_data, output_file, last_file):
        self.printer.line_comment("General Information")

        process_name = j_data['target']['file']['name']
        if process_name not in self.process_list:
            self.process_list.append(process_name)
            j_analysis_started = j_data['info']['started']
            j_analysis_ended = j_data['info']['ended']

            self.printer.line_comment("Process Behaviour")

            signature_dict = self.map_signatures(j_data)
            seen_first, seen_last, tracked_dict = self.get_tracked_process(j_data, True)

            self.printer.line_comment("Writing report for: " + process_name)

            general_dict = {
                "file_name": name,
                "binary_name": process_name,
                "date_time_analysis": j_analysis_started,
                "duration_analysis": self.tools.time_diff(j_analysis_started, j_analysis_ended),
                "duration_sample": self.tools.time_diff(seen_first, seen_last),
                "seen_first": seen_first,
                "seen_last": seen_last,
                "signatures": signature_dict,
                "tracked_processes": tracked_dict
            }

            self.printer.write_file(output_file, '"%s": %s%c' %
                                    (name,
                                     json.dumps(general_dict, sort_keys=True, indent=4),
                                     ',' if not last_file else ' '))

    def parse_files(self, p_dir, output_file):
        # loop over files in a directory,
        # ref: https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
        self.printer.write_file(output_file, '{')
        for (dir_path, dir_names, file_names) in walk(p_dir):
            for i, name in enumerate(file_names):
                if name.endswith('.json'):
                    self.printer.line_comment("Read and parse from json file: " + name)
                    # open json data and load it
                    with open(dir_path + name) as json_file:
                        j_data = json.load(json_file)
                    
                    self.parse_data(name, j_data, output_file, False if i < len(file_names) - 1 else True)

        self.printer.write_file(output_file, '}')
