#! /usr/bin/env python

import glob
from argparse import ArgumentParser

# It's ok to have the same gene, it's not ok to have different genes
# >10001_OD25_Stylurus_spiniceps_A15_assembly_comp31414_c0_seq1_2-325_-_
def read_headers(infile) :
    ''' Returns bool and a dictionary in this schema -- {species} -> [genes(no isoform id)]
    Parameters :
        infile : string
    '''
    fasta_map = {}
    header = ''
    fh = open(infile, 'r')
    for line in fh :
        if line[0] == '>' :
            header = line.strip()
            species = '%s_assembly' %'_'.join(header.split('_')[1:]).split('_assembly')[0]
            gene = '_'.join(header.split('assembly_')[1].split('_')[:2])
            if species not in fasta_map :
                # First time species seen.
                fasta_map[species] = set()
                fasta_map[species].add(gene)
            elif gene not in fasta_map[species] :
                # We know the species was seen, and it was a different gene.
                return False, None
    fh.close()
    return True, fasta_map

def main(bin) :
    options = []
    for infile in glob.glob('*bin%d.aln' %bin) :
        good, genes = read_headers(infile)
        if good :
            options.append(infile)
    print('%d potentially conserved clusters.' %len(options))
    print('Output in potential_1to1.txt')
    ofh = open('potential_1to1.txt', 'w')
    ofh.write('\n'.join(options))
    ofh.close()

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('bin', metavar='number_of_species', type=int)
    args = parser.parse_args()
    main(args.bin)
    print('Done.')
