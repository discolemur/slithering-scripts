#! /usr/bin/env python

import sys
import re
import glob
import os
import subprocess
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update

nowhere = open(os.devnull, 'w')

def info() :
    print('This program must be run inside a directory of clusters (output from multihamstr.py)')
    print('and puts the clusters (conserved or semi) into their own directory, aligned.')

regex = re.compile('.*OD10.*|.*OD12.*|.*OD36.*|.*OD64.*')

def is_conserved(file, num_sp) :
    global regex
    file_handle = open(file, 'r')
    species = set()
    result = True
    for line in file_handle :
        if line[0] == '>' :
            sp = line.split('|')[2]
            if regex.match(sp) :
                if sp in species and result :
                    print('Fail by paralogy')
                    result = False
                    break
                species.add(sp)
    file_handle.close()
    if result and len(species) != num_sp :
        print('Fail by len(species) %d' %len(species))
        result = False
    return result

def is_valid(file, num_sp) :
    return is_conserved(file, num_sp)

def handle_file(file, num_sp, dir) :
    global nowhere
    if is_valid(file, num_sp) :
        new_name = file.split('.')[0] + '.aln'
        subprocess.call("mafft %s > %s/%s" %(file, dir, new_name), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)

def align_files(files, num_sp) :
    dir = 'ODconserved_clusters'
    if not os.path.exists(dir) :
        os.makedirs(dir)
    do_progress_update(files, handle_file, num_sp, dir)

def main() :
    info()
    files = glob.glob('*.fa')
    align_files(files, 4)
    return 0

if __name__ == '__main__' :
    main()
