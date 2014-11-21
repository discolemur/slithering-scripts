#! /usr/bin/env python

import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from find_one_to_one_clusters import get_one_to_ones
from argparse import ArgumentParser
import subprocess
import glob


def main(num_sp) :
    files = glob.glob('*.fa')
    for file in get_one_to_ones(files, num_sp) :
        alnfile = '%s.aln' %file.split('.')[0]
        print(alnfile)
        subprocess.call('mafft --auto \'%s\' > \'%s\'' %(file, alnfile), shell=True)

if __name__=='__main__' :
    parser = ArgumentParser()
    parser.add_argument('num_sp', type=int)
    args = parser.parse_args()
    main(args.num_sp)
