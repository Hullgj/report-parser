from __future__ import print_function

import sys
import argparse
from classifier import Classify
from parser import Parse
from printer import Print


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

    # printer.write_file(output_file, '', 'w')

    parser = Parse(printer)
    # parser.parse_files(p_dir, output_file)

    in_dir = "docs/"
    in_file = "classify.json"
    classifier = Classify(printer)
    classifier.classify(output_file, in_dir, in_file)


if __name__ == "__main__":
    sys.exit(main())
