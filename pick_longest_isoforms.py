#! /usr/bin/env python

import glob
from argparse import ArgumentParser

def get_species(header) :
    if 'assembly' in header :
        return '%s_assembly' %'_'.join(header.split('_')[1:]).split('_assembly')[0]
    else :
        return header.split('_')[1]

def get_gene(header) :
    '''
    This is the most important function in this script.
    Here is where we parse the gene id from the header.
    It is important to get the gene id and not the isoform id.
    '''
    if 'assembly' in header :
        return '_'.join(header.split('assembly_')[-1].split('_')[:2])
    else :
        return '_'.join(header.split('fastq-out_')[-1].split('_')[:2])

# >0_dyak100_1.fastq.dyak100_2.fastq-out_c6216_g1_i2_m.7442
# >10001_OD25_Stylurus_spiniceps_A15_assembly_comp31414_c0_seq1_2-325_-_
def read_fasta(infile) :
    ''' Returns a dictionary in this schema -- {species} -> {genes(no isoform id)} -> {isoform_header} -> sequence
    Parameters :
        infile : string
    '''
    fasta_map = {}
    header = ''
    fh = open(infile, 'r')
    species = ''
    gene = ''
    header = ''
    for line in fh :
        line = line.strip()
        if line[0] == '>' :
            header = line
            species = get_species(header)
            print(species)
            gene = get_gene(header)
            if species not in fasta_map :
                # First time species seen.
                fasta_map[species] = {}
            if gene not in fasta_map[species] :
                fasta_map[species][gene] = {}
            if header not in fasta_map[species][gene] :
                fasta_map[species][gene][header] = ''
            else :
                print('HUGE ERROR! Duplicate headers.')
        else :
            fasta_map[species][gene][header] += line.replace('-','').upper()
    fh.close()
    return fasta_map

def main(infile, ext) :
    files = []
    if infile == '.' :
        files = glob.glob('*%s' %ext)
    else :
        ifh = open(infile, 'r')
        files = [ line.strip() for line in ifh if len(line.strip()) != 0 ]
        ifh.close()
    if len(files) == 0 :
        print('Found no fasta files to read.')
    for infasta in files :
        fasta = read_fasta(infasta)
        ofh = open('%s.no_iso.fasta' %infasta.replace('.aln',''), 'w')
        for sp in fasta :
            for gene in fasta[sp] :
                best_seq = ''
                best_header = ''
                for header in fasta[sp][gene] :
                    if len(fasta[sp][gene][header]) > len(best_seq) :
                        best_seq = fasta[sp][gene][header]
                        best_header = header
                ofh.write('%s\n%s\n' %(best_header, best_seq))
        ofh.close()

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('-f', help='File with list of cluster files, where each file is on a different line.', default='.')
    parser.add_argument('-e', help='Extension to use to locate fasta files (-f overrides this).', default='aln')
    args = parser.parse_args()
    print('\nThis program selects the largest isoform for each gene.')
    print('Change the get_gene function if you discover that it is not successfully keeping one copy per gene.')
    print('This script does not modify the original file.')
    print('By default, this program finds all *.aln files in the directory, then makes a *.no_iso.fasta file.')
    print('The -f argument allows you to use a file (containing a list of fasta files) to modify.')
    print('The -e argument defines the file extension for this program to read (ex: fasta, fa, aln)\n')
    main(args.f, args.e)
    print('Done.')
