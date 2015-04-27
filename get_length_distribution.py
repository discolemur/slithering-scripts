#! /usr/bin/env python

import glob
import sys

# Report a distribution for the lengths of alignments

# We only need to read one sequence, because it is aligned (they are all the same length.)
def aln_len(file) :
    fh = open(file, 'r')
    seq = ''
    while True :
        line = fh.readline().strip()
        if line[0] == '>' :
            if len(seq) != 0 :
                fh.close()
                return len(seq)
        else :
            seq += line

def main(outfile) :
    lengths = []
    for file in glob.glob('*.aln') :
        lengths.append( (file, str(aln_len(file))) )
    fh = open(outfile, 'w')
    fh.write('\n'.join([ '%s\t%s' %(file, length) for file, length in lengths ]))
    fh.close()

if __name__ == '__main__' :
    if len(sys.argv) != 2 :
        print('Usage: %s output_filename' %sys.argv[0])
        exit(1)
    main(sys.argv[1])
