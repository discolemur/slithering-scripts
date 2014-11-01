#! /usr/bin/env python

import glob
import subprocess
import os
import threading
import argparse

def trim_file(filename, trimmed_fasta) :
    fh = open('tmp%s' %filename, 'w')
    for header in trimmed_fasta :
        fh.write('%s\n%s\n' %(header, trimmed_fasta[header]))
    fh.close()
    subprocess.call('mafft tmp%s > %s' %(filename, filename), shell=True)
    os.remove('tmp%s' %filename)

def handle_file(file) :
    fasta = {}
    header = ''
    fh = open(file, 'r')
    for line in fh :
        line = line.strip()
        if line[0] == '>' :
            header = line
            fasta[header] = ''
        else :
            fasta[header] += line.replace('-', '')
    fh.close()
    good = True
    fasta_keys = list(fasta.keys())
    for header in fasta_keys :
        if len(fasta[header]) == 0 :
            del fasta[header]
            good = False
    if not good :
        print('bad %s' %file)
        trim_file(file, fasta)

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

def main(num_threads) :
    files = glob.glob('*.aln')
    run_threads(num_threads, files)

if __name__=='__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='Number of threads.', type=int, default=1)
    args = parser.parse_args()
    main(args.t)
