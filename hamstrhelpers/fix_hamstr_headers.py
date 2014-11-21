#! /usr/bin/env python

import sys
import shutil
import glob

# >466|RPROL|R_EP_006_assembly|comp8494_c0_seq2_199_1341_+|1

def parse_header(line) :
    spl = line[1:].split('|')
    return '%s.%s.%s.%s' %(spl[0], spl[2], spl[3], spl[4])

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
    files = glob.glob('*.fa')
    for file in files : handle_file(file)

if __name__ == "__main__" :
    main(sys.argv)
