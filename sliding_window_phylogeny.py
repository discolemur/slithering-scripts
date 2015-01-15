#! /usr/bin/env python

import sys
import subprocess
from argparse import ArgumentParser

def read_fasta(infile) :
    ''' Returns a dictionary in this schema -- {header_string} -> [ sequence_string ]
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

def check_fasta(fasta) :
    ''' Returns a dictionary {header_string} -> sequence_string

    Parameters :
        fasta : (the output of read_fasta)
    Makes sure there is only one sequence per header in the fasta.
    Exits the program if not.
    '''
    for header in fasta :
        if len(fasta[header]) != 1 :
            sys.stderr.write(' oops. The input fasta cannot contain duplicate headers, buddy.\n')
            exit(1)
        fasta[header] = fasta[header][0]
    return fasta

def write_batch(filename) :
    ''' Returns batch name (string)
    Parameter :
        filename -- name of fasta file
    '''
    batch = '%s.sh' %filename
    fh = open(batch, 'w')
    fh.write('#!/bin/bash\n#SBATCH --time=05:00 --ntasks=6\n')
    fh.write('#SBATCH --nodes=1 --mem-per-cpu=200M -J %s\n' %filename)
    fh.write('/fslhome/njensen6/software/bin/iqtree-omp -omp 6 -m TEST -s %s\n' %filename)
    fh.close()
    return batch

def write_files(fasta, start, width) :
    ''' Returns batch name (string)

    Parameters :
        fasta : output of check_fasta
        start : position of start of window (int)
        width : size of window (int)
    Writes the fasta file and calls a function to write the batch.
    '''
    filename = 'supersmall%d.fasta' %start
    fh = open(filename, 'w')
    for header in fasta :
        fh.write('%s\n%s\n' %(header, fasta[header][start:start+width]))
    fh.close()
    return write_batch(filename)

def get_trees(fasta, width) :
    ''' Returns None
    Parameters :
        fasta : output of check_fasta
        width : size of sliding window (int)
    Slides window, calls function to write fasta and batch for window, and submits batch to get tree.
    '''
    full_width = len(list(fasta.values())[0])
    for i in range(full_width - width + 1) :
        batch = write_files(fasta, i, width)
        subprocess.call(['sbatch', batch])

def main(infile, width) :
    fasta = read_fasta(infile)
    fasta = check_fasta(fasta)
    get_trees(fasta, width)
    exit(0)

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('width', help = 'Width of sliding window', type = int)
    args = parser.parse_args()
    sys.stdout.write('Working...')
    main(args.infile, args.width)
    sys.stdout.write(' done.\n')
