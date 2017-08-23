"""
* author: Gavin Hull
* version: 2017.08.22
* description: This is the main function that instantiates and calls methods for printing, parsing, and classifying. It
ends by generating graphs of all JSON files in the specified directory.
"""

from __future__ import print_function

import argparse
import sys
from os import walk

from classifier import Classify
from graphs.plotter import Plot
from parsing import Parser
from tools.printer import Printer


def main():
    parser = argparse.ArgumentParser(description="process all JSON files in the given directory"
                                                 "outputting the results in the given filename")
    parser.add_argument("parse_dir", help="enter the directory to parse")
    parser.add_argument("output_file", help="enter the file where the results will be written")
    parser.add_argument("-v", "--verbose", action="store_true", help="set verbose output")
    parser.add_argument("-s", "--skip", action="store_true", help="skip parsing the files")
    args = parser.parse_args()

    if args.verbose:
        printer = Printer(True)
    else:
        printer = Printer(False)

    p_dir = args.parse_dir
    output_file = args.output_file

    if not args.skip:
        printer.standard_output('Chosen directory %s. Wait for file: %s to be generated' % (p_dir, output_file))
        printer.standard_output('verbose is set to: %r' % printer.get_verbose())

        printer.write_file(output_file, '', 'w')

        parsing = Parser(printer)
        parsing.parse_files(p_dir, output_file)

    in_dir = "docs/"
    in_file = "classify.json"
    classifier = Classify(printer)
    classifier.classify(output_file, in_dir, in_file)

    type = 'apis'
    cat_dir = 'docs/randep-binary-maps/%s/' % type
    grap_dir = 'docs/randep-binary-maps/graphs/'
    plotter = Plot()
    for (dir_path, dir_names, file_names) in walk(cat_dir):
        for i, name in enumerate(file_names):
            if name.endswith('.json'):
                printer.line_comment("Generate graph from json file: " + name)
                api_names, start_times, end_times, state_names, state_starts, state_ends, class_names, class_starts, class_ends = \
                    classifier.get_api_data(dir_path + name, type)
                plotter.plots(grap_dir + 'apis/' + name, api_names, start_times, end_times)
                plotter.plots(grap_dir + 'states/' + name, state_names, state_starts, state_ends)
                plotter.plots(grap_dir + 'classes/' + name, class_names, class_starts, class_ends)


if __name__ == "__main__":
    sys.exit(main())
