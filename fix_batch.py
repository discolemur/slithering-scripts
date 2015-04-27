#! /usr/bin/env python

import glob
import shutil

# Just a handy way of fixing the sbatch requirements in submission scripts.
# You are free to tweak this according to your needs.

def fix_batch(file) :
    tmp = '%s.tmp' %file
    ifh = open(file, 'r')
    ofh = open(tmp, 'w')
    ofh.write('#!/bin/bash\n\n')
    ofh.write('#SBATCH --time=50:00:00   # walltime\n')
    ofh.write('#SBATCH --ntasks=8   # number of processor cores (i.e. tasks)\n')
    ofh.write('#SBATCH --nodes=1   # number of nodes\n')
    ofh.write('#SBATCH --mem-per-cpu=1G   # memory per CPU core\n')
    ofh.write('#SBATCH -J iqtree_%s   # job name\n' %file[:-3])
    for line in ifh :
        if line[0] != '#' :
            ofh.write(line)
    ofh.close()
    ifh.close()
    shutil.move(tmp, file)

for file in glob.glob('cluster*.sh') :
    fix_batch(file)

