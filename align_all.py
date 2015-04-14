#! /usr/bin/env python

import argparse
import threading
import os
import subprocess
import glob

# this is to silence mafft
nowhere = open(os.devnull, 'w')
def align(filename) :
    global nowhere
    subprocess.call("mafft %s > %s" %(filename, filename.replace('.fasta', '.aln')), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
    os.remove(filename)

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

def main(num_threads) :
    print('Handling *.fasta')
    run_threads(num_threads, glob.glob('*.fasta'), align)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='Number of threads.', type=int, default=1)
    args = parser.parse_args()
    main(args.t)
    print('Done.')

