#! /usr/bin/env python

import argparse

# HEADER FORMATS:
#     PEP
# >cds.c28295_g1_i1|m.21446 c28295_g1_i1|g.21446  ORF c28295_g1_i1|g.21446 c28295_g1_i1|m.21446 type:internal len:352 (-) c28295_g1_i1:2-1054(-)
#     CDS (Weird -- the term "cds." only appears in the pep file.)
# >c28295_g1_i1|m.21446 c28295_g1_i1|g.21446  ORF c28295_g1_i1|g.21446 c28295_g1_i1|m.21446 type:internal len:352 (-) c28295_g1_i1:2-1054(-)

def extract_by_ids(fasta, ids) :
    out_fasta = '%s.no_duplicates' %fasta
    ifh = open(fasta, 'r')
    ofh = open(out_fasta, 'w')
    get = False
    for line in ifh :
        # We use the id as a switch, deciding whether to get the sequence or not
        if line[0] == '>' :
            if line.strip().split(' ')[-1] in ids :
                get = True
            else :
                get = False
        if get :
            ofh.write(line)
    ofh.close()
    ifh.close()

def read_ids(fasta) :
    ids = set()
    ifh = open(fasta, 'r')
    for line in ifh :
        if line[0] == '>' :
            ids.add(line.strip().split(' ')[-1])
    ifh.close()
    return ids

def main(pep_file, dna_file) :
    ids = read_ids(pep_file)
    extract_by_ids(dna_file, ids)

if __name__ == '__main__' :
    print('Working')
    parser = argparse.ArgumentParser()
    parser.add_argument('pep_file')
    parser.add_argument('dna_file')
    args = parser.parse_args()
    main(args.pep_file, args.dna_file)
    print('Done.')

