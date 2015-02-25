#! /usr/bin/env python

import glob
import sys

def aln_len(file) :
    fh = open(file, 'r')
    fasta = {}
    for line in fh :
        line = line.strip()
        if line[0] == '>' :
            header = line
            fasta[header] = ''
        else :
            fasta[header] += line
    fh.close()
    return len(fasta[list(fasta.keys())[0]])

def main(outfile) :
    lengths = []
    for file in glob.glob('*.aln') :
        lengths.append(str(aln_len(file)))
    fh = open(outfile, 'w')
    fh.write(' '.join(lengths))
    fh.close()

if __name__ == '__main__' :
    if len(sys.argv) != 2 :
        print('Usage: %s output_filename' %sys.argv[0])
        exit(1)
    main(sys.argv[1])
