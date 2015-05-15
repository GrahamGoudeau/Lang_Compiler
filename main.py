from __future__ import print_function
from tokenize import * 
from parse_token import *
import sys

argv = sys.argv

INPUT_INDEX = 1

def main():
    file = get_source(argv[INPUT_INDEX])

    code = file.read()
    check_parens(code)

    tokenized = tokenize(code)

    func_map = make_function_map(iter(tokenized), tokenized)
    if False:
        for f in func_map:
            for t in func_map[f].def_block:
                print(t.symbol)

    # check if the parse succeeds;
    # is_parsed fails with sys.exit() and message if parse error
    if is_parsed(func_map):
        #compile(func_map)
        pass

    file.close()

def get_source(file_name):
    try:
        file = open(file_name, 'r')
    except IOError:
        print("Problem with file: {0}".format(file_name), file=sys.stderr)
        sys.exit()
    return file


if __name__ == "__main__":
    main()
