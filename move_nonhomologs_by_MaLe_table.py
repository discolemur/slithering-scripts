#! /usr/bin/env python

import os
import sys
import glob
import shutil
import argparse

__author__='njensen6'

''' INPUT FORMAT
-bash-4.1$ less hamstr_MaLe_log_reg_output.txt 

!=== Predictions on test data ===
! inst#     actual  predicted error prediction (id)
     1        1:?        1:H       1 (1001)
     2        1:?        1:H       1 (1006)
     3        1:?        1:H       1 (1005)
     4        1:?       2:NH       1 (1002)
     5        1:?        1:H       1 (1004)
     6        1:?        1:H       1 (1010)
     7        1:?        1:H       1 (1011)
     8        1:?        1:H       1 (1003)
     9        1:?        1:H       1 (1014)
    10        1:?        1:H       1 (1013)
'''

def is_non_homologous(row) :
    if row[2] == '2:NH' :
        return True
    elif row[2] == '1:H' :
        return False
    else :
        print('OH NO! UNKNOWN HOMOLOGY! Will not move it.')
        return False

def move_cluster(infile, in_dir, out_dir) :
    print('Moving %s' %infile)
    shutil.move(infile, out_dir)

def main(infile, in_dir) :
    out_dir = 'non_homologs'
    if not os.path.isdir(out_dir) :
        os.mkdir(out_dir)
    rows = [line.strip().split() for line in open(infile, 'r') if len(line) != 1 and line[0] != '!' ]
    H = set()
    NH = set()
    for row in rows :
        if is_non_homologous(row) :
            NH.add('%s.aln' %row[-1][1:-1])
        else :
            H.add('%s.aln' %row[-1][1:-1])
    files = glob.glob('%s/*.aln' %in_dir)
    for file in files :
        name = file.split('/')[-1]
        if name in NH :
            move_cluster(file, in_dir, out_dir)
        elif name not in H :
            print('Unknown cluster: %s' %file)

if __name__=='__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('MaLe_file')
    parser.add_argument('in_dir')
    args = parser.parse_args()
    main(args.MaLe_file, args.in_dir)
