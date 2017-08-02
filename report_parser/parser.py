import json
from os import walk

from tools import Tools


class Parse(object):

    def __init__(self, printer):
        self.printer = printer
        self.tools = Tools()

    def map_signatures(self, json_data):
        """Parse the signatures in the JSON file, mapping each to a state in the probabilistic model"""
        api_dict = {}

        for signature in json_data['signatures']:
            set_call = False
            set_category = False
            set_entropy = False
            set_other = False
            api_dict[ signature['name'] ] = {'description': signature['description']}  # initial assignment
            this_api_dict = api_dict[ signature['name'] ]
            this_api_dict['detections'] = signature['markcount']

            # if len(signature['marks']) > 0:
            #     if 'call' in signature['marks'][0]:
            #         this_api_dict['indicators'] = {'timestamps': []}
            #     if 'category' in signature['marks'][0]:
            #         this_api_dict['indicators'] = {'ioc': []}
            #     if 'entropy' in signature['marks'][0]:
            #         this_api_dict['indicators'] = {'entropy': [], 'description': []}
            #     else:
            #         this_api_dict['indicators'] = {'other': []}
            #         self.printer.line_comment("Either no marks in %s or mark is unregistered" % signature)

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
                else:

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
        name
        DEV: might need to count the number of times the process was called"""
        api_dict = {}
        process_name = ""
        seen_first = 0
        seen_last = 0

        for process in json_data['behavior']['processes']:
            if process['track'] == condition:
                process_name = process['process_name']
                seen_first = process['first_seen']
                for call in process['calls']:
                    if call['api'] not in api_dict:
                        api_dict[call['api']] = call['time']
                    else:
                        api_dict[call['api'] + ' - p_end'] = call['time']

                    if seen_last < call['time']:
                        seen_last = call['time']

                # api_dict = sorted(api_dict.items(), key=operator.itemgetter(1))

        return process_name, seen_first, seen_last, api_dict

    def parse_data(self, j_data, output_file):
        self.printer.line_comment("General Information")

        j_analysis_started = j_data['info']['started']
        j_analysis_ended = j_data['info']['ended']

        self.printer.line_comment("Process Behaviour")

        signature_dict = self.map_signatures(j_data)
        process_name, seen_first, seen_last, tracked_dict = self.get_tracked_process(j_data, True)

        self.printer.line_comment("Writing report for: " + process_name)

        general_dict = {
            "binary_name": process_name,
            "date_time": j_analysis_started,
            "duration_analysis": self.tools.time_diff(j_analysis_started, j_analysis_ended),
            "duration_sample": self.tools.time_diff(seen_first, seen_last)
        }

        self.printer.write_file(output_file, "general: %s" % json.dumps(general_dict, sort_keys=True, indent=4))
        self.printer.write_file(output_file, "Detected signatures: %s" %
                                json.dumps(signature_dict, sort_keys=True, indent=4))
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
