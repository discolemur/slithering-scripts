#! /usr/bin/env python

import sys
import itertools

# Commandline arg is input peptide file.
if len(sys.argv) == 1 :
    print('Please provide a file to check.')
    exit(1)

codons = [''.join(codon) for codon in itertools.product('ATGC', repeat=3)]

infile = sys.argv[1]

fh = open(infile, 'r')
total = 0.0
big_map = {}
codon = ''
for line in fh :
    line = line.strip()
    if line[0] == '>' :
        if len(codon) != 0 :
            print('Huge error! A sequence was not divisible by three.')
    if line[0] != '>' :
        line = line.upper()
        for char in line :
            codon += char
            if len(codon) == 3 :
                total += 1
                if codon not in big_map :
                    big_map[codon] = 0
                big_map[codon] += 1
                codon = ''
fh.close()

if len(codon) != 0 :
    print('Huge error! A sequence was not divisible by three.')

for codon in codons :
    percent = 0
    if codon in big_map :
        percent = big_map[codon] / total
    sys.stdout.write('%f\t' %percent)
sys.stdout.write('\n')
