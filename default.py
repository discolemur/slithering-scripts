#! /usr/bin/env python

from argparse import ArgumentParser

def read_fasta(infile) :
    ''' Returns a dictionary in this schema -- {header(string)} -> [ sequence(string) ]
    Parameters :
        infile : string
    '''
    fasta_map = {}
    header = ''
    fh = open(infile, 'r')
    for line in fh :
        line = line.strip()
        if line[0] == '>' :
            header = line
            if header not in fasta_map :
                fasta_map[header] = []
            fasta_map[header].append('')
        else :
            fasta_map[header][-1] += line
    fh.close()
    return fasta_map

def main(infile) :
    fasta = read_fasta(infile)

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('infile')
    args = parser.parse_args()
    main(args.infile)
