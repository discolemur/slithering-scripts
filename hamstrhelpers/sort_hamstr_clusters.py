#! /usr/bin/env python

from argparse import ArgumentParser
import glob
import shutil
import os

def has_paralogs(cluster) :
    for sp in cluster :
        if len(cluster[sp]) > 1 :
            return True
    return False

def is_one_to_one(cluster, num_sp) :
    # No gene loss
    if len(list(cluster.keys())) != num_sp :
        return False
    # No paralogs
    if has_paralogs(cluster) :
        return False
    # Yay!
    return True

def get_sp(line) :
    return line.split('.')[1]

def read_file(file) :
    genes = {}
    sp = ''
    for line in open(file, 'r'):
        if line[0] == '>' :
            sp = get_sp(line)
            if sp not in genes :
                genes[sp] = []
            genes[sp].append(line)
    return genes

def make_dir(dir) :
    if not os.path.isdir(dir) :
        os.mkdir(dir)

# In an attempt to standardize headers
def change_header(line) :
    line = line.replace('|', '_')
    line = line.replace(':', '_')
    line = line.replace('(', '_')
    line = line.replace(')', '_')
    line = line.replace('.', '_')
    line = line.replace('RPROL_', '')
    return line

def copy_file(file, newdir) :
    ifh = open(file, 'r')
    outfile = '%s/%s' %(newdir, file.split('/')[-1])
    ofh = open(outfile, 'w')
    for line in ifh :
        if line[0] == '>' :
            ofh.write(change_header(line))
        else :
            ofh.write(line)
    ofh.close()
    ifh.close()

def sort_files(files, num_sp) :
    dir1to1 = 'conserved'
    make_dir(dir1to1)
    dirsemi = 'semiconserved'
    make_dir(dirsemi)
    dirothers = 'not_semiconserved'
    make_dir(dirothers)
    for file in files :
        cluster = read_file(file)
        if is_one_to_one(cluster, num_sp) :
            # Copy file to 1to1 and semiconserved
            copy_file(file, dir1to1)
            copy_file(file, dirsemi)
        elif not has_paralogs(cluster) :
            # Copy file to semiconserved
            copy_file(file, dirsemi)
        else :
            # Copy file to others
            copy_file(file, dirothers)
 
def main(num_sp) :
    files = glob.glob('*.fa')
    counter = 0
    sort_files(files, num_sp)

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('num_sp', help='Number of species.', type=int)
    args = parser.parse_args()
    main(args.num_sp)
    print('Done.')
