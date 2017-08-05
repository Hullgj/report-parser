"""Classifier identifies detected signatures and properties of an analysed sample and groups each per sample into
defined categories. The categories are based on the RanDep model, consisting of eight states: fingerprinting,
propagation, communication with C&C, mapping the user's files and folders, encryption, locking the OS, deleting files,
and producing a threatening message. This program reads data parsed from Cuckoo Sandbox reports, looks up names of APIs
using Microsoft's online documentation, and writes each detection into one of the eight states in a JSON format"""

import subprocess
import json

class Classifier(object):

    def __init__(self, printer):
        self.printer = printer

    def get_api_class(self, api):
        """check if the api already has a class, if not, search online and put it in an appropriate one"""

        print subprocess.Popen(
            "casperjs kent-uni-project-code/web_scraper/microsoft_api_scraper.js " + api, shell=True,
            stdout=subprocess.PIPE).stdout.read()

    def classify(self, input_dir, input_file):
        """read the parse data file and pass each api call to get its category"""
        api = 0
        with open(input_dir + input_file) as json_file:
            p_data = json.load(json_file)

        for binary in p_data['binaries']:
            for api in binary['tracked_processes']:
                self.get_api_class(api)

        self.printer('classify.data', 'w')
