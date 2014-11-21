#! /usr/bin/env python

import argparse
import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from get_columns_from_supermatrix import main
import glob
import subprocess
import os


def write_batch(file) :
    batch = '%s.sh' %file
    fh = open(batch, 'w')
    fh.write('#!/bin/bash\n')
    fh.write('#SBATCH --time=120:00:00\n#SBATCH --ntasks=32\n')
    fh.write('#SBATCH --nodes=1\n#SBATCH --mem-per-cpu=8G\n')
    fh.write('#SBATCH -J "iqtree"\n')
    fh.write('/fslgroup/fslg_BybeeLab/software/iqtree-omp-0.9.6-Linux/bin/iqtree -bb 1000 -m TEST -s \'%s\'\n' %file)
    fh.close()
    return batch

def run(supermatrix, numcols, numreps, dir) :
    if not os.path.exists(dir) :
        os.makedirs(dir)
    main(supermatrix, numcols, numreps, dir)
    # At this point, take each file and run iqtree
    files = glob.glob('%s/columns*.aln' %dir)
    for file in files :
        batch = write_batch(file)
        subprocess.call('sbatch %s' %batch, shell=True)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('supermatrix', metavar='supermatrix.fasta')
    parser.add_argument('numcols', metavar='#columns', type=int)
    parser.add_argument('numreps', metavar='#repetitions', type=int)
    parser.add_argument('dir', metavar='output_directory')
    args = parser.parse_args()
    run(args.supermatrix, args.numcols, args.numreps, args.dir)

