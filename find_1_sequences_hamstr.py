#! /usr/bin/env python

import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update
import glob

# Takes all hamstr clusters, creates a new file inside only_1s/ directory that has only the best hit ortholog for each organism in that cluster (the ones with "1" at the end of the header line)
# That essentially removes all paralogs from the hamstr output.


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
