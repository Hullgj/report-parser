from __future__ import print_function


class Print(object):

    def __init__(self, verbose):
        self.verbose = verbose

    def set_verbose(self, condition):
        self.verbose = condition

    def get_verbose(self):
        return self.verbose

    def print_error(self, error_line):
        if self.verbose:
            print(error_line)

    # make a comment that takes up a whole line
    def line_comment(self, msg):
        if self.verbose:
            print(10 * '-' + 5 * '+' + ' ' + msg + ' ' + 5 * '+' + 10 * '-')

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
