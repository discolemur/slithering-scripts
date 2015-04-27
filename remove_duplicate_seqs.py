#! /usr/bin/env python

import glob
import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update
import argparse

# Removes duplicate sequences from fasta file.

# Only use this if you need to use transdecoder output, and want it simplified.
# Example header from transdecoder:
# >cds.comp10002_c0_seq1|m.12725 comp10002_c0_seq1|g.12725  ORF comp10002_c0_seq1|g.12725 comp10002_c0_seq1|m.12725 type:5prime_partial len:406 (+) comp10002_c0_seq1:3-1220(+)
def parse_header(line) :
    #return line[1:].split('.')[1].split('|')[0]
    return line

def write_output(seqs, filename) :
    outfile = open(filename + '.no_duplicates', 'w')
    for seq in seqs :
        outfile.write('%s\n%s\n' %(seqs[seq], seq))
    outfile.close()

def removeDuplicates(filename) :
    log = open('%s.log' %filename, 'w')
    file = open(filename, 'r')
    id = ''
    header = ''
    seq = ''
    # map from sequence to header
    seqs = {}
    num_duplicates = 0
    for line in file :
        line = line.strip()
        if line[0] == '>' :
            if id != '' and seq != '' and header != '':
                if seq not in seqs :
                    seqs[seq] = header
                else :
                    log.write('%s is the same as %s\n' %(id, parse_header(seqs[seq])))
                    num_duplicates += 1
                id = ''
                seq = ''
            id = parse_header(line)
            header = line
            seq = ''
        else :
            if line[-1] == '*' :
                line = line[:-1]
            seq = seq + line
    file.close()
    log.close()
    if num_duplicates > 0 :
        write_output(seqs, filename)
    print('%s\t%d' %(filename, num_duplicates))
    return num_duplicates

def main(args) :
    parser = argparse.ArgumentParser()
    parser.add_argument('extension', help='Common file extensions include fasta, pep, fa, aln, aa, and fas.')
    args = parser.parse_args()
    extension = args.extension
    files = glob.glob('*%s' %extension)
    do_progress_update(files, removeDuplicates)

if __name__ == '__main__' :
    main(sys.argv)
