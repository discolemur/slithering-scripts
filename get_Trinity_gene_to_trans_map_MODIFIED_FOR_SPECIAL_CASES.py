#!/usr/bin/env python

import sys

# >c0_g1_i1 len=253 path=[577:0-15 337:16-252]

# first is the fasta
# second is the output

ifh = open(sys.argv[1])
ofh = open(sys.argv[2], 'w')
for line in ifh :
    if line[0] != '>' :
        continue
    trans = line[1:].split(' ')[0]
    gene = '_'.join(trans.split('_')[:2])
    ofh.write("%s\t%s\n" %(gene, trans))
ofh.close()
ifh.close()
