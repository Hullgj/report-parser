"""Classifier identifies detected signatures and properties of an analysed sample and groups each per sample into
defined categories. The categories are based on the RanDep model, consisting of eight states: fingerprinting,
propagation, communication with C&C, mapping the user's files and folders, encryption, locking the OS, deleting files,
and producing a threatening message. This program reads data parsed from Cuckoo Sandbox reports, looks up names of APIs
using Microsoft's online documentation, and writes each detection into one of the eight states in a JSON format"""

from __future__ import division
import subprocess
import json


class Classify(object):
    def __init__(self, printer):
        self.printer = printer
        self.categories = {
            "stealth": {"fingerprinting": {}, "propagating": {}, "communicating": {}, "mapping": {}},
            "suspicious": {"encrypting": {}, "locking": {}},
            "termination": {"deleting": {}, "threatening": {}}
        }
        self.classify_d = None

    def search_list(self, api_list, n):
        """Use the web scraper script built using CasperJS to search and return the category of every API in the list.
         Since each search takes time, we limit each search to groups of 10 APIs in the list"""
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

    def get_api_class(self, api_list, n):
        """Check if the api already has a class, if not, search online and put it in an appropriate one. We map all
        detected APIs with their Microsoft category and call the categories with their found APIs along with any data
        in the parse data JSON file, such as timestamps and count. api_lookup_list makes sure only non categorised
        APIs are searched for online. The results are combined based on the category as the key. """
        api_lookup_list = []
        for api_name in api_list:
            if all([api_name not in self.classify_d['apis'], api_name not in api_lookup_list]):
                api_lookup_list.append(api_name)
            else:
                api_cat_dic = self.classify_d['apis'][api_name]
                self.printer.line_comment("API " + api_name + " already indexed and classified as " + api_cat_dic)

        err_search_list, api_cat_dic = self.search_list(api_lookup_list, n)

        if err_search_list < (len(api_lookup_list) / n):
            for api in api_cat_dic:
                # Add the api : cat to the classify_json dict. The api_lookup_list has the APIs and their properties
                # from the cuckoo reports with key as the API. The api_cat_dic has the APIs and their categories from
                #  the web scraper.
                self.classify_d['apis'][api] = next(iter(api_cat_dic[api]))
                # Add the cat : { api : { api_prop } to the classify_json dict. The api_cat_dict has the cat,
                # where keys are APIs; so loop through api_cat_dict adding each api with the category as the
                # resultant key, and the api as the value, along with the additional properties of the search result.
                cat_name = next(iter(api_cat_dic[api]))
                if cat_name not in self.classify_d['categories']:
                    self.classify_d['categories'][cat_name] = {api: api_cat_dic[api][cat_name]}
                else:
                    self.classify_d['categories'][cat_name][api] = api_cat_dic[api][cat_name]
                # Add the properties from api_cat_dic and api_list
                for api_prop in api_list[api]:
                    self.classify_d['categories'][cat_name][api][api_prop] = api_list[api][api_prop]

        self.printer.standard_output(api_cat_dic)

        return err_search_list, api_cat_dic

    def process_apis(self, parser_d):
        """Get a list of all APIs in all binaries and get their category from Microsoft using the web scraper."""
        api_list = {}
        for binary in parser_d:
            for api in parser_d[binary]['tracked_processes']:
                api_list[api] = parser_d[binary]['tracked_processes'][api]

        # Look up the APIs in groups of n, if there is an error, n will be decreased by a factor of 2
        n = 5
        while n:
            err, category = self.get_api_class(api_list, n)
            n = (n / 2 if err > 1 else 0)

    def set_category(self, c_data, c_group, r_group):
        """Map the categories to the classes of the RanDep model, eliminating any categories
        that do not fit, such as Tool Helper Functions. Input the dictionary of classify_json['categories'], and add
        each one that matches a category in the randep dictionary under the matched category's parent"""
        r_data = self.printer.open_json('docs/randep-skeleton.json')
        # print [(r_cat, r_class, c_cat) for c_cat in c_dict[r_group] for r_class in r_dict for r_cat in r_dict[r_class]
        # if c_cat in r_dict[r_class][r_cat][r_group]]
        for c_cat in c_data[c_group]:
            for r_class in r_data:
                for r_cat in r_data[r_class]:
                    if c_cat in r_data[r_class][r_cat][r_group]:
                        if r_group not in self.categories[r_class][r_cat]:
                            self.categories[r_class][r_cat][r_group] = {c_cat: c_data[c_group][c_cat]}
                        else:
                            self.categories[r_class][r_cat][r_group][c_cat] = c_data[c_group][c_cat]

        # write the file with the c_group as the name, which should be the name_of_the_binary.json
        self.printer.write_file('docs/randep-binary-maps' + c_group.replace("\.","-") + '.json',
                                json.dumps(self.categories, sort_keys=True, indent=4),
                                'w')

    def map_binaries(self, parser_d, class_d):
        mapped_d = {}
        for binary in parser_d:
            mapped_d[binary] = {}
            for api in parser_d[binary]['tracked_processes']:
                if api in class_d['apis']:
                    category = class_d['apis'][api]
                    if category not in mapped_d[binary]:
                        mapped_d[binary][category] = {api: parser_d[binary]['tracked_processes'][api]}
                    else:
                        mapped_d[binary][category][api] = parser_d[binary]['tracked_processes'][api]
            self.set_category(mapped_d, binary, 'categories')

    def classify(self, input_file, out_dir, out_file):
        """Read the parse data file and pass each api call to get its category. Then from the parse data copy each api
        and its values into its relevant category"""

        parse_d = self.printer.open_json(input_file)

        self.classify_d = self.printer.open_json(out_dir + out_file, obj_list=['apis', 'categories'])

        self.process_apis(parse_d)

        # self.set_category(api, category)
        self.printer.write_file(out_dir + out_file, json.dumps(self.classify_d, sort_keys=True, indent=4), 'w')

        self.set_category(self.classify_d, 'categories', 'categories')

        # per binary, loop through signatures, and APIs.
        self.map_binaries(parse_d, self.classify_d)
