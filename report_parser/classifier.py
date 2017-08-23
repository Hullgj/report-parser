"""
* author: Gavin Hull
* version: 2017.08.22
* short description: Taking a JSON/dictionary of binaries from Parse() class, classify each API into the RanDep model
* description: Classifier identifies detected signatures and properties of an analysed sample and groups each per sample into
defined categories. The categories are based on the RanDep model, consisting of eight states: fingerprinting,
propagation, communication with C&C, mapping the user's files and folders, encryption, locking the OS, deleting files,
and producing a threatening message. This program reads data parsed from Cuckoo Sandbox reports, looks up names of APIs
using Microsoft's online documentation, and writes each detection into one of the eight states in a JSON format
"""

from __future__ import division
import subprocess
import json
from tools.tools import Tools


class Classify(object):
    def __init__(self, printer):
        """
        On initialisation of the Classify class we get the handle of the printer class from the instantiating function
        and store it, then we make the categories bare bone, which is a RanDep skeleton
        :param printer: the handle of the Printer class
        """
        self.printer = printer
        self.tools = Tools()
        self.categories = {
            "stealth": {"fingerprinting": {}, "propagating": {}, "communicating": {}, "mapping": {}},
            "suspicious": {"encrypting": {}, "locking": {}},
            "termination": {"deleting": {}, "threatening": {}}
        }
        # self.classify_d = None

    def search_list(self, api_list, n):
        """
        Use the web scraper script built using CasperJS to search and return the category of every API in the list.
         Since each search takes time, we limit each search to groups of 5 APIs in the list, but this can be set as
         wished.
        :param api_list: the list of APIs to search and index
        :param n: the size of the group to search using the web scraper
        :return: the number of errors per API counted from the web scraper, and the search results as a JSON object
        """
        err_count = 0
        full_list = api_list
        search_results = ''
        if not api_list:
            return err_count, search_results
        elif api_list > n:
            search_results = "{ "
            api_list = [full_list[i:i + n] for i in range(0, len(full_list), n)]
            # api_list = api_list[:2]

        self.printer.line_comment("Search List has %d APIs to lookup in segments of %d"
                                  % (len(full_list), len(api_list)))

        for i, list_seg in enumerate(api_list):
            join_seg = " ".join(list_seg)
            self.printer.line_comment("Searching for %d / %d APIs, including: %s"
                                      % ((i + 1) * len(list_seg), len(full_list), join_seg))
            s_result_seg = subprocess.Popen("casperjs web_scraper/microsoft_api_scraper.js "
                                            + join_seg, shell=True, stdout=subprocess.PIPE).stdout.read()
            if 'Error:' not in s_result_seg:
                search_results += s_result_seg + (',' if (i + 1) * n < len(full_list) else '}')
            else:
                self.printer.print_error("Error for segment %s. Try running the program again to scrape those"
                                         " results.\n%s" % (join_seg, s_result_seg))
                err_count += 1

            if any(['cat_not_found' in s_result_seg, s_result_seg == '']):
                self.printer.dev_comment("The scraper didn't find the category, we could use the Bing or Google scraper"
                                         " instead.\nHowever, this might need to get the category from the 'See also' "
                                         "section of the web page")

        search_results = search_results.replace("\n", "")
        return err_count, json.loads(search_results)

    def get_api_class(self, classify_d, api_list, n):
        """
        Check if the API already has a class, if not, search online and put it in an appropriate one. We map all
        detected APIs with their Microsoft category and call the categories with their found APIs along with any data
        in the parse data JSON file, such as timestamps and count. api_lookup_list makes sure only non categorised
        APIs are searched for online. The results are combined based on the category as the key.
        :param classify_d: the JSON data / dictionary for reading and writing classification data
        :param api_list: the list of APIs to lookup and then add to the classify_d dictionary
        :param n: the size of the group of APIs to search for in the web scraper
        :return: the number of errors from searching, the JSON object of the search results, and the classify data that
        has been populated with the new and original data of the API:Categories, and Categories:{API:{info}}
        """
        api_lookup_list = []
        classify = classify_d
        for api_name in api_list:
            if all([api_name not in classify['apis'], api_name not in api_lookup_list]):
                api_lookup_list.append(api_name)
            else:
                api_cat_dic = classify['apis'][api_name]
                self.printer.line_comment("API " + api_name + " already indexed and classified as " + api_cat_dic)

        err_search_list, api_cat_dic = self.search_list(api_lookup_list, n)

        if err_search_list < (len(api_lookup_list) / n):
            for api in api_cat_dic:
                # Add the api : cat to the classify_json dict. The api_lookup_list has the APIs and their properties
                # from the cuckoo reports with key as the API. The api_cat_dic has the APIs and their categories from
                #  the web scraper.
                classify['apis'][api] = next(iter(api_cat_dic[api]))
                # Add the cat : { api : { api_prop } to the classify_json dict. The api_cat_dict has the cat,
                # where keys are APIs; so loop through api_cat_dict adding each api with the category as the
                # resultant key, and the api as the value, along with the additional properties of the search result.
                cat_name = next(iter(api_cat_dic[api]))
                if cat_name not in classify['categories']:
                    classify['categories'][cat_name] = {api: api_cat_dic[api][cat_name]}
                else:
                    classify['categories'][cat_name][api] = api_cat_dic[api][cat_name]
                # Add the properties from api_cat_dic and api_list
                for api_prop in api_list[api]:
                    classify['categories'][cat_name][api][api_prop] = api_list[api][api_prop]

        self.printer.standard_output(api_cat_dic)

        return err_search_list, api_cat_dic, classify

    def process_apis(self, parser_d, classify_d):
        """
        Get a list of all APIs in all binaries and get their category from Microsoft using the web scraper.
        :param parser_d: the dictionary that has the processed data from the Parser class of all the binaries
        :param classify_d: the dictionary that holds the information about known APIs and their categories
        :return: the classify data dictionary after getting information from get_api_class() function
        """
        api_list = {}
        classify = classify_d
        for binary in parser_d:
            for api in parser_d[binary]['tracked_processes']:
                api_list[api] = parser_d[binary]['tracked_processes'][api]

        # Look up the APIs in groups of n, if there is an error, n will be decreased by a factor of 2
        n = 5
        while n:
            err, category, classify = self.get_api_class(classify_d, api_list, n)
            n = (n / 2 if err > 1 else 0)

        return classify

    def map_randep(self, mapped_cats, binary, info_type, _filename):
        """
        Map the categories to the classes of the RanDep model, eliminating any categories
        that do not fit, such as Tool Helper Functions. Input the dictionary of classify_json['categories'], and add
        each one that matches a category in the randep dictionary under the matched category's parent
        This function loads the RanDep model from the file docs/randep-model/team_classify.json, which holds a JSON
        dictionary of the states and classes of the predicted behaviour of ransomware.
        :param mapped_cats contains the data to be classified with the RanDep model
        :param binary name of the binary sample
        :param info_type the type of information being added for classification
        :param _filename the name of the file where the RanDep model is stored
        """
        randep_model = {
            "stealth": {"fingerprinting": {}, "propagating": {}, "communicating": {}, "mapping": {}},
            "suspicious": {"encrypting": {}, "locking": {}},
            "termination": {"deleting": {}, "threatening": {}}
        }
        randep_data = self.printer.open_json('%s' % _filename)
        # add general information to the RanDep model
        randep_model['general'] = mapped_cats[binary]['general']

        for category in mapped_cats[binary]:
            for _class in randep_data:
                for state in randep_data[_class]:
                    if info_type is 'categories':
                        # if the binary's category is in the RanDep model
                        if category in randep_data[_class][state][info_type]:
                            if info_type not in randep_model[_class][state]:
                                randep_model[_class][state][info_type] = {category: mapped_cats[binary][category]}
                            else:
                                randep_model[_class][state][info_type][category] = mapped_cats[binary][category]
                    elif info_type is 'apis':
                        for api in mapped_cats[binary][category]:
                            # if the binary's api is in the RanDep model
                            if api in randep_data[_class][state][info_type]:
                                if info_type not in randep_model[_class][state]:
                                    randep_model[_class][state][info_type] = {api: mapped_cats[binary][category][api]}
                                else:
                                    randep_model[_class][state][info_type][api] = mapped_cats[binary][category][api]

        # write the file with the binary as the name, which should be the name_of_the_binary.json
        self.printer.write_file('docs/randep-binary-maps/' + info_type + '/' +
                                mapped_cats[binary]['general']['file_name'].replace(".", "-") + '.json',
                                json.dumps(randep_model, sort_keys=True, indent=4),
                                'w')

    def map_binaries(self, parser_d, class_d):
        """
        Map for each binary in the parser data file, with the category from the classify data file.
        Then send the mapped categories to be mapped against the RanDep model.
        :param parser_d: the parse data from the Parse class, this has the information for each sample/binary analysed
        in Cuckoo Sandbox
        :param class_d: the classify data that has been classified in this class, Classify, containing the categories
        :return:
        """
        mapped_cats = {}
        parsed = parser_d
        classify = class_d
        for binary in parsed:
            mapped_cats[binary] = {}
            # add the general information to mapped_cats
            mapped_cats[binary]['general'] = {
                "file_name": parsed[binary]["file_name"],
                "binary_name": parsed[binary]["binary_name"],
                "date_time_analysis": parsed[binary]["date_time_analysis"],
                "duration_analysis": parsed[binary]["duration_analysis"],
                "duration_sample": parsed[binary]["duration_sample"],
                "seen_first": parsed[binary]["seen_first"],
                "seen_last": parsed[binary]["seen_last"]
            }
            for api in parsed[binary]['tracked_processes']:
                # if the API has a Microsoft category stored in classify
                if api in classify['apis']:
                    # get the category name
                    category = classify['apis'][api]
                    # if that category is not already stored in mapped_cats then make a new dict then add it
                    if category not in mapped_cats[binary]:
                        mapped_cats[binary][category] = {api: classify['categories'][category][api]}
                    else:
                        mapped_cats[binary][category][api] = classify['categories'][category][api]

                    timestamps = parsed[binary]['tracked_processes'][api]['timestamps']
                    mapped_cats[binary][category][api]['timestamps'] = timestamps
                    mapped_cats[binary][category][api].pop('timestamps', None)
                    mapped_cats[binary][category][api]['count'] = parsed[binary]['tracked_processes'][api]['count']
                    mapped_cats[binary][category][api]['called_first'] = min(timestamps)
                    mapped_cats[binary][category][api]['called_last'] = max(timestamps)
            # map the categories of the binary, which is now stored in mapped_cats, with those of the RanDep model
            self.map_randep(mapped_cats, binary, 'categories', 'docs/randep-model/randep-skeleton.json')
            # map the APIs of the binary, which is now stored in mapped_cats, with those of the RanDep model
            self.map_randep(mapped_cats, binary, 'apis', 'docs/randep-model/team_classify.json')

    def get_api_data(self, _filename, type):
        """
        Open the file as JSON data and get useful information, usually for generating and graph. This is built for
        RanDep classified JSON files
        :param _filename: the filename to get the data from
        :return: as lists the API names, start times, end times. This is built for RanDep classified JSON files
        """
        api_data = self.printer.open_json(_filename)

        # api_names, class_names, state_names, start_times, end_times = \
        #     zip(*[[api,
        #            next(iter(api_data[_class])),
        #            state,
        #            api_data[_class][state][type][api]['called_first'],
        #            api_data[_class][state][type][api]['called_last']]
        #           for _class, state in api_data.iteritems()
        #           # for state in api_data[_class]
        #           if type in api_data[_class][state]
        #           for api in api_data[_class][state][type]])

        api_names = []
        class_names = []
        state_names = []
        start_times = []
        end_times = []
        class_starts = []
        class_ends = []
        state_starts = []
        state_ends = []
        for _class in api_data:
            if _class != 'general':
                start_temp_class = []
                end_temp_class = []
                class_start_tmp = 0
                class_end_tmp = 0
                for state in api_data[_class]:
                    if type in api_data[_class][state]:
                        start_temp = []
                        end_temp = []
                        state_start_tmp = 0
                        state_end_tmp = 0
                        # get the API data for this state
                        for api in api_data[_class][state][type]:
                            called_first = self.tools.time_diff_s(
                                api_data['general']['seen_first'],
                                api_data[_class][state][type][api]['called_first']
                            )
                            called_last = self.tools.time_diff_s(
                                api_data['general']['seen_first'],
                                api_data[_class][state][type][api]['called_last']
                            )
                            if called_last < called_first:
                                self.printer.print_error("Called first is earlier that called last. "
                                                         "API: %s, state: %s, called_first: %s, called_last: %s" %
                                                         (api, state, called_first, called_last))
                            start_temp.append(called_first)
                            end_temp.append(called_last)
                            state_start_tmp = min(start_temp)
                            state_end_tmp = max(end_temp)
                            # set the API data for this API
                            api_names.append(api)
                            start_times.append(called_first)
                            end_times.append(called_last)

                        start_temp_class.extend(start_times)
                        end_temp_class.extend(end_times)
                        class_start_tmp = min(start_temp_class)
                        class_end_tmp = max(end_temp_class)
                        # set the state data for this class
                        state_names.append(state)
                        state_starts.append(state_start_tmp)
                        state_ends.append(state_end_tmp)

                # set the class data for this api
                class_names.append(_class)
                class_starts.append(class_start_tmp)
                class_ends.append(class_end_tmp)

        return api_names, start_times, end_times, state_names, state_starts, state_ends, class_names, class_starts, class_ends

    def classify(self, input_file, out_dir, out_file):
        """
        Read the parse data file and pass each api call to get its category. Then from the parse data copy each api
        and its values into its relevant category
        :param input_file: the file containing the parse data from the Parse class
        :param out_dir: the directory to write the classified data to
        :param out_file: the filename to write the classified data to
        :return:
        """

        parse_d = self.printer.open_json(input_file)

        classify_d = self.printer.open_json(out_dir + out_file, obj_list=['apis', 'categories'])

        classify_d = self.process_apis(parse_d, classify_d)

        self.printer.write_file(out_dir + out_file, json.dumps(classify_d, sort_keys=True, indent=4), 'w')

        # for all binaries, map the categories to the RanDep model
        # self.map_randep(classify_d, 'categories', 'categories', 'docs/randep-model/randep-skeleton.json')

        # per binary, loop through signatures, and APIs.
        self.map_binaries(parse_d, classify_d)
