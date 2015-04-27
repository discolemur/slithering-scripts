#! /usr/bin/env python

import sys
import shutil
import glob

# Changes headers to be the last item in the header (split by space)
# > This is the big long header stuff.
# Would become
# >stuff.

def parse_header(line) :
    if len(line.split(' ')) == 1 :
        return line[1:]
    return line[1:].split(' ')[-1]

def handle_file(file) :
    tmp = '%s.tmp' %file
    input = open(file, 'r')
    out = open(tmp, 'w')
    for line in input :
        line = line.strip()
        if line[0] == '>' :
            out.write('>%s\n' %parse_header(line))
        else :
            out.write('%s\n' %line)
    input.close()
    out.close()
    shutil.move(tmp, file)
    return 0

def main(args) :
    files = glob.glob('*.pep')
    for file in files : handle_file(file)

if __name__ == "__main__" :
    main(sys.argv)
