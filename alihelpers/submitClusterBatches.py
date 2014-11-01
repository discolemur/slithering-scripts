#! /usr/bin/env python

import argparse
import threading
import os
import subprocess
import glob

limit = 4999
def queue_has_room():
    global limit
    size = int(subprocess.check_output('squeue -u njensen6 | wc -l', shell=True).split()[0])
    pending = int(subprocess.check_output('squeue -u njensen6 | grep \'.*Ali.*PD.*\' | wc -l', shell=True).split()[0])
    running = int(subprocess.check_output('squeue -u njensen6 | grep \'.*Ali.*R.*\' | wc -l', shell=True).split()[0])
    # We say if only 25% are running, we don't add to the queue.
    if pending > (3 * running) :
        return False
    if size < limit :
        return True
    return False

def handle_file(batch) :
    file = '%s' %batch.split('Batch.sh')[0]
    print('Trying file %s' %file)
    list = '%s_List_random.txt' %file
    if os.path.isfile(list) :
        os.remove(batch)
        print('List exists.')
        return
    if queue_has_room() :
        subprocess.call(['sbatch',batch])
    else :
        subprocess.call('./%s' %batch, shell=True)
    if os.path.isfile(list) :
        os.remove(batch)

def handle_files(files) :
    for file in files :
        handle_file(file)

def run_threads(num_threads, files) :
    print('Creating threads')
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

def main(dir, num_threads) :
    os.chdir(dir)
    print('Getting *Batch.sh')
    files = glob.glob('*Batch.sh')
    print('Found %d batches.' %len(files))
    run_threads(num_threads, files)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='directory name', default = '.')
    parser.add_argument('-t', help='Number of threads.', type=int, default=1)
    args = parser.parse_args()
    limit = 4999 - args.t
    main(args.d, args.t)


