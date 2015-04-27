#! /usr/bin/env python

# This script  removes dangling '*' from the sequences

import sys

def usage(filename) :
    print('Usage: ')
    print(filename + ' <fasta in> <fasta out>')

def main(args) :
    if len(args) != 3 :
        usage(args[0])
    fasta_in = open(args[1], 'r')
    fasta_out = open(args[2], 'w')
    line = ''
    for line in fasta_in :
        line = line.strip()
        if line[0] == '>' :
            fasta_out.write(line)
        else :
            if line[-1] == '*' :
                line = line[:-1]
            fasta_out.write(line)
    if line != '' :
        fasta_out.write('\n')
    fasta_out.close()
    fasta_in.close()

if __name__ == "__main__" :
    main(sys.argv)
