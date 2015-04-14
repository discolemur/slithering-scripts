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



-bash-4.1$ less inparanoid_semiconserved_logistic_regression.txt

!=== Predictions on test data ===
! inst#     actual  predicted error prediction (id)
     1        1:?        1:H       1 (cluster500_bin2)
     2        1:?        1:H       1 (cluster515_bin2)
     3        1:?        1:H       1 (cluster10360_bin15)
     4        1:?        1:H       1 (cluster10362_bin15)
     5        1:?        1:H       1 (cluster10479_bin15)
     6        1:?        1:H       0.789 (cluster10359_bin15)
     7        1:?        1:H       1 (cluster10763_bin17)
     8        1:?        1:H       1 (cluster10760_bin17)
     9        1:?        1:H       1 (cluster10370_bin15)
    10        1:?       2:NH       1 (cluster10516_bin15)
'''

def is_non_homologous(row) :
    if row[2] == '2:NH' :
        return True
    elif row[2] == '1:H' :
        return False
    else :
        print('OH NO! UNKNOWN HOMOLOGY! Will not move it.')
        print(row)
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
    # ALICUT_cluster1000_bin2.aln
    for row in rows :
        if is_non_homologous(row) :
            NH.add('%s' %row[-1][1:-1])
        else :
            H.add('%s' %row[-1][1:-1])
    files = glob.glob('%s/*.aln' %in_dir)
    for file in files :
        name = ''
        if 'ALICUT_' in name :
            name = file.split('/')[-1].split('ALICUT_')[1].split('.aln')[0]
        else :
            name = file.split('/')[-1].split('.aln')[0]
        #name = file.split('/')[-1].split('.aln')[0]
        if name in NH :
            move_cluster(file, in_dir, out_dir)
        elif name not in H :
            print('Unknown cluster: %s, %s' %(file, name))

if __name__=='__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('MaLe_file')
    parser.add_argument('in_dir')
    args = parser.parse_args()
    main(args.MaLe_file, args.in_dir)
