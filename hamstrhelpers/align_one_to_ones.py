#! /usr/bin/env python

import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from find_one_to_one_clusters import check_all_files
from argparse import ArgumentParser
import subprocess
import glob


def main(num_sp) :
    files = glob.glob('*.fa')
    for file in check_all_files(files, num_sp, False) :
        alnfile = '%s.aln' %file.split('.')[0]
        print(alnfile)
        subprocess.call('mafft --auto \'%s\' > \'%s\'' %(file, alnfile), shell=True)

if __name__=='__main__' :
    parser = ArgumentParser()
    parser.add_argument('num_sp', type=int)
    args = parser.parse_args()
    main(args.num_sp)
