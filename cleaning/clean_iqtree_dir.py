#! /usr/bin/env python

import argparse
import threading
import os
import subprocess
import glob

def handle_file(file) :
    batch = '%s.sh' %file
    treefile = '%s.treefile' %file
    if os.path.isfile(treefile) and os.path.isfile(batch) :
        os.remove(batch)
        print('Removed %s' %batch)

def handle_files(files) :
    for file in files :
        handle_file(file)

def run_threads(num_threads, files) :
    threads = []
    div = int(len(files) / num_threads)
    begin = 0
    end = div + (len(files) % num_threads)
    for i in range(num_threads) :
        thread = threading.Thread(target=handle_files, args=(files[begin:end],))
        threads.append(thread)
        thread.start()
        begin = end
        end += div
    for thread in threads :
        thread.join()

def remove_all(files) :
    for file in files :
        os.remove(file)

''' Example files
ALICUT_cluster265_bin20.aln          
ALICUT_cluster265_bin20.aln.bionj     
ALICUT_cluster265_bin20.aln.contree    
ALICUT_cluster265_bin20.aln.initial_tree
ALICUT_cluster265_bin20.aln.iqtree
ALICUT_cluster265_bin20.aln.jcdist
ALICUT_cluster265_bin20.aln.log   
ALICUT_cluster265_bin20.aln.mldist
ALICUT_cluster265_bin20.aln.model  
ALICUT_cluster265_bin20.aln.rate    
ALICUT_cluster265_bin20.aln.sh       
ALICUT_cluster265_bin20.aln.splits    
ALICUT_cluster265_bin20.aln.splits.nex 
ALICUT_cluster265_bin20.aln.treefile
'''

def remove_by_regex(expression) :
    print('Removing %s' %expression)
    remove_all(glob.glob(expression))

def main(dir, num_threads) :
    os.chdir(dir)
    remove_by_regex('slurm-*')
    remove_by_regex('*.bionj')
    remove_by_regex('*.initial_tree')
    remove_by_regex('*.jcdist')
    remove_by_regex('*.mldist')
    remove_by_regex('*.rate')
    remove_by_regex('*.splits*')
    print('Handling *.aln')
    files = glob.glob('*.aln')
    run_threads(num_threads, files)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='directory name', default = '.')
    parser.add_argument('-t', help='Number of threads.', type=int, default=1)
    args = parser.parse_args()
    main(args.d, args.t)

