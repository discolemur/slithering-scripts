#! /usr/bin/env python

import sys
import glob
import subprocess
import random
from argparse import ArgumentParser

random.seed()

def check_fasta(fasta) :
    ''' Returns a dictionary {header_string} -> sequence_string

    Parameters :
        fasta : {header_string} -> [ sequence_string ]
    Makes sure there is only one sequence per header in the fasta.
    Exits the program if not.
    '''
    for header in fasta :
        if len(fasta[header]) != 1 :
            sys.stderr.write(' oops. The input fasta cannot contain duplicate headers, buddy.\n')
            exit(1)
        fasta[header] = fasta[header][0]
    return fasta

def read_fasta(infile) :
    ''' Returns a dictionary in this schema -- {header_string} -> sequence_string
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
    fasta_map = check_fasta(fasta_map)
    return fasta_map

def write_batch(filename) :
    ''' Returns batch name (string)
    Parameter :
        filename -- name of fasta file
    '''
    batch = '%s.sh' %filename
    fh = open(batch, 'w')
    fh.write('#!/bin/bash\n#SBATCH --time=10:00 --ntasks=6\n')
    fh.write('#SBATCH --nodes=1 --mem-per-cpu=100M -J %s\n' %filename)
    fh.write('/fslhome/njensen6/software/bin/iqtree-omp -omp 6 -m TEST -s %s\n' %filename)
    fh.close()
    return batch

def write_files(fasta, start, width, infile) :
    ''' Returns batch name (string)

    Parameters :
        fasta : output of read_fasta
        start : position of start of window (int)
        width : size of window (int)
    Writes the fasta file and calls a function to write the batch.
    '''
    filename = 'window.%s' %infile
    fh = open(filename, 'w')
    for header in fasta :
        fh.write('%s\n%s\n' %(header, fasta[header][start:start+width]))
    fh.close()
    return write_batch(filename)

def main(width) :
    files = glob.glob('super*.fasta')
    full_width = len(list(read_fasta(files[0]).values())[0])
    start = random.randint(0, full_width - width)
    for file in files :
        fasta = read_fasta(file)
        batch = write_files(fasta, start, width, file)
        subprocess.call(['sbatch', batch])

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('width', help = 'Width of sliding window', type = int)
    args = parser.parse_args()
    sys.stdout.write('Working...')
    main(args.width)
    sys.stdout.write(' done.\n')
