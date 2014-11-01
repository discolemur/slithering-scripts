#! /usr/bin/env python

import argparse
import threading
import os
import subprocess
import glob

def handle_file(file) :
    aln = '%s.aln' %file.split('.aln')[0]
    batch = '%sBatch.sh' %aln
    if os.path.isfile(batch) :
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

def main(dir, num_threads) :
    os.chdir(dir)
    print('Removing slurm-*')
    remove_all(glob.glob('slurm-*'))
    print('Removing *.svg')
    remove_all(glob.glob('*.svg'))
    print('Removing *Profile_random.txt')
    remove_all(glob.glob('*Profile_random.txt'))
    print('Handling *List*')
    files = glob.glob('*List*')
    run_threads(num_threads, files)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='directory name', default = '.')
    parser.add_argument('-t', help='Number of threads.', type=int, default=1)
    args = parser.parse_args()
    main(args.d, args.t)

