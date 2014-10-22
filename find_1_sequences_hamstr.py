#! /usr/bin/env python

import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update
import glob

dir = 'only_1s'

def handle_file(file) :
    global dir
    fasta_map = {}
    fh = open(file, 'r')
    header = ''
    for line in fh :
        if line.strip() == '' :
            continue
        if line[0] == '>' :
            header = line
            fasta_map[header] = ''
        elif header != '' :
            fasta_map[header] += line
    fh.close()
    fh = open('%s/%s' %(dir, file), 'w')
    for header in fasta_map :
        if header.strip()[-1] == '1' :
            fh.write(header)
            fh.write(fasta_map[header])
    fh.close()

def main() :
    files = glob.glob('*fa*')
    do_progress_update(files, handle_file)


if __name__ == '__main__' :
    main()
