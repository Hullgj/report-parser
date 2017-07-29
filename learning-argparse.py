# REF: https://docs.python.org/2/howto/argparse.html#id1
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("parse_dir", help="enter the directory to parse")
parser.add_argument("output_file", help="enter the file where the results will be written")
parser.add_argument("-v", "--verbose", help="turn verbosity on", action="store_true")
args = parser.parse_args()
if args.verbose:
    print "verbose output enabled"

p_dir = args.parse_dir
output_file = args.output_file
print('Chosen directory %s. Wait for file: %s to be generated' % (p_dir, output_file))