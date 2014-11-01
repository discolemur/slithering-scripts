#! /usr/bin/env python

import sys
import shutil
import glob

files = glob.glob('pep_all_OD-R_EP_01_06/*.sh')

#perl Aliscore.02.2.pl -i 3166.aln

for file in files :
    fh = open(file, 'r')
    out = open('tmp', 'w')
    out.write('#!/bin/bash\n')
    out.write('#SBATCH --time=1:00:00 --ntasks=1 --nodes=1 --mem-per-cpu=8G -J Ali\n')
    for line in fh :
        if line == '' :
            continue
        if line[0] != '#' :
            out.write(line)
    out.close()
    fh.close()
    shutil.move('tmp', file)

