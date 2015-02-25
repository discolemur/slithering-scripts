#! /usr/bin/env python

import argparse
import random

random.seed()

def load_into_memory(supermatrix) :
    sm = {}
    with open(supermatrix, 'r') as fh :
        header = ''
        for line in fh :
            line = line.strip()
            if line[0] == '>' :
                header = line[1:]
                sm[header] = ''
            elif header != '' :
                sm[header] += line
    return sm , sorted(list(sm.keys()))

def get_columns(numcols, sm, species, seqlen) :
    res = {}
    cols = sorted(random.sample(range(seqlen), numcols))
    for sp in species :
        res[sp] = ''.join([sm[sp][x] for x in cols])
    return res

def write_columns(cols_map, outfile, dir) :
    with open('%s/%s' %(dir, outfile), 'w') as fh :
        for sp in cols_map :
            fh.write('>%s\n%s\n' %(sp, cols_map[sp]))

def main(supermatrix, numreps, percent_cols, dir) :
    sm , species = load_into_memory(supermatrix)
    seqlen = len(sm[species[0]])
    numcols = int(seqlen * percent_cols)
    print('There are %d columns.' %numcols)
    truncated = supermatrix.split('.')[0][:8]
    for i in range(1, numreps + 1) :
        cols_map = get_columns(numcols, sm, species, seqlen)
        outfile = '%d_cols_%s_%d.aln' %(numcols, truncated, i)
        write_columns(cols_map, outfile, dir)

if __name__ == '__main__' :
    print('This program samples some % of the supermatrix\'s columns and builds a tree based on those columns.')
    parser = argparse.ArgumentParser()
    parser.add_argument('supermatrix', metavar='supermatrix.fasta')
    parser.add_argument('numreps', metavar='#repetitions', type=int)
    parser.add_argument('percent', metavar='percent_columns_to_use(decimal)', type=float)
    parser.add_argument('-dir', metavar='output_directory', default='.')
    args = parser.parse_args()
    main(args.supermatrix, args.numreps, args.percent, args.dir)
