#! /usr/bin/env python

import sys

# This is to fix the get_gene_to_trans_map issue in the trinotate pipeline.
# It may or may not work in every case.
# Feel free to tweak it however necessary.

file = sys.argv[1]

# >contig00009  gene=isogroup00001  length=884 

fh = open(file, 'r')
ofh = open('%s.gene_trans_map' %file, 'w')
for line in fh :
    if line[0] == '>' :
        line = line[1:].split()
        gene = 'BOGUS_FACE1'
        trans = 'BOGUS_FACE2'
        if len(line) == 1 :
            gene = line[0]
            trans = gene
        else :
            trans = line[0]
            gene = line[1].split('=')[1]
        ofh.write('%s\t%s\n' %(gene, trans))
ofh.close()
fh.close()
