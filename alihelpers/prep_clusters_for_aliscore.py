#! /bin/env python

import argparse
import shutil
import glob
import threading

def change_header(line) :
    line = line[1:]
    line = line.replace('|', '_')
    line = line.replace(':', '_')
    line = line.replace('(', '_')
    line = line.replace(')', '_')
    return line

def handle_file(file) :
    tmp = '%s.tmp' %file
    input = open(file, 'r')
    out = open(tmp, 'w')
    for line in input :
        line = line.strip()
        if line[0] == '>' :
            out.write('>%s\n' %change_header(line))
        else :
            out.write('%s\n' %line.replace('X', '-'))
    input.close()
    out.close()
    shutil.move(tmp, file)
    return 0

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

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='Number of threads.', type=int, default=1)
    args = parser.parse_args()
    main(args.t)
