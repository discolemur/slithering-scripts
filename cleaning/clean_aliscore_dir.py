#! /usr/bin/env python

import argparse
import threading
import os
import subprocess
import glob

def handle_List_file(file) :
    aln = '%s.aln' %file.split('.aln')[0]
    batch = '%sBatch.sh' %aln
    if os.path.isfile(batch) :
        os.remove(batch)
#        print('Removed %s' %batch)

def handle_batch_file(batch) :
    aln = batch[:-8]
    list_file = '%s_List_random.txt' %aln
    if os.path.isfile(list_file) :
        os.remove(batch)
#        print('Removed %s' %batch)

def handle_individual_files(files, task) :
    for file in files :
        task(file)

def run_threads(num_threads, files, task) :
    threads = []
    div = int(len(files) / num_threads)
    begin = 0
    end = div + (len(files) % num_threads)
    for i in range(num_threads) :
        thread = threading.Thread(target=handle_individual_files, args=(files[begin:end],task,))
        threads.append(thread)
        thread.start()
        begin = end
        end += div
    for thread in threads :
        thread.join()

def main(dir, num_threads) :
    os.chdir(dir)
    print('Removing slurm-*')
    run_threads(num_threads, glob.glob('slurm-*'), os.remove)
    print('Removing *.svg')
    run_threads(num_threads, glob.glob('*.svg'), os.remove)
    print('Removing *Profile_random.txt')
    run_threads(num_threads, glob.glob('*Profile_random.txt'), os.remove)
    print('Handling *.sh')
    run_threads(num_threads, glob.glob('*.sh'), handle_batch_file)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='directory name', default = '.')
    parser.add_argument('-t', help='Number of threads.', type=int, default=1)
    args = parser.parse_args()
    main(args.d, args.t)
    print('Done.')

