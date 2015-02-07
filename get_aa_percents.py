#! /usr/bin/env python

import sys

# Commandline arg is input peptide file.
peps = list('ACDEFGHIKLMNPQRSTVWY')

if len(sys.argv) == 1 :
    print('Please provide a file to check.')
    exit(1)

infile = sys.argv[1]

fh = open(infile, 'r')
total = 0.0
big_map = {}
for line in fh :
    line = line.strip()
    if line[0] != '>' :
        for aa in line :
            total += 1
            if aa not in big_map :
                big_map[aa] = 0
            big_map[aa] += 1
fh.close()

for aa in peps :
    percent = 0
    if aa in big_map :
        percent = big_map[aa] / total
    sys.stdout.write('%f\t' %percent)
sys.stdout.write('\n')
