#! /usr/bin/env python

import sys

file = sys.argv[1]

# >contig00009  gene=isogroup00001  length=884 

fh = open(file, 'r')
ofh = open('%s.gene_trans_map' %file, 'w')
for line in fh :
    if line[0] == '>' :
        line = line[1:].split()
        gene = 'BOGUS_FACE'
        trans = 'a'
        if len(line) == 1 :
            gene = line[0]
        else :
            trans = line[0]
            gene = line[1].split('=')[1]
        ofh.write('%s\t%s\n' %(gene, trans))
ofh.close()
fh.close()
