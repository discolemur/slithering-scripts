#! /usr/bin/env python

import threading
from argparse import ArgumentParser
import glob

def get_sp(line) :
    line = line.split('_assembly')[0]
    if '|' in line :
        sp = line.split('|')[1]
    elif '_' in line :
        sp = '_'.join(line.split('_')[1:])
    else :
        print('Couldn\'t parse the species, sorry.')
    return sp

# ONE-TO-ONE:
#    Do not allow gene loss, do not allow gene duplication.
# SEMICONSERVED:
#    Allow gene loss, do not allow gene duplication.
def check_file(infile, num_sp, semicon) :
    # This is to check for paralogs
    names = set()
    # This is to test for gene loss
    non_blanks = set()
    sp = ''
    seq = ''
    fh = open(infile, 'r')
    for line in fh:
        line = line.strip()
        if line[0] == '>' :
            if len(seq) != 0 :
                non_blanks.add(sp)
            sp = get_sp(line)
            seq = ''
            # No paralogs (gene duplication)
            if sp in names :
                #print('Has paralog %s' %sp)
                return False
            names.add(sp)
        else :
            seq += line.replace('-', '')
    fh.close()
    if len(seq) != 0 :
        non_blanks.add(sp)
    # No gene loss (conserved)
    if len(list(non_blanks)) != num_sp and not semicon :
        #print('Has gene loss %d' %len(list(non_blanks)))
        return False
    return True

# Depreciated
def check_all_files(files, num_sp, semicon) :
    for file in files :
        if check_file(file, num_sp, semicon) :
            yield file

def handle_files(files, results, begin, end, num_sp, semicon) :
    for i in range(begin, end) :
        file = files[i]
        if check_file(file, num_sp, semicon) :
            results[i] = file

def run_threads(num_threads, files, num_sp, semicon) :
    results = [ None for i in range(len(files)) ]
    threads = []
    div = int(len(files) / num_threads)
    begin = 0
    end = div + (len(files) % num_threads)
    for i in range(num_threads) :
        thread = threading.Thread(target=handle_files, args=(files, results, begin, end, num_sp, semicon, ))
        threads.append(thread)
        thread.start()
        begin = end
        end += div
    for thread in threads :
        thread.join()
    return results
 
def main(num_sp, nthread, semicon) :
    files = glob.glob('*.aln')
    if len(files) == 0 :
        files = glob.glob('*.fasta')
    if len(files) == 0 :
        print('No files found.')
        ext = input('What is the file extension to use? (aln, fasta, fa, pep) :')
        files = glob.glob('*%s' %ext)
        if len(files) == 0 :
            print('Sorry, you lose.')
            exit(1)
    counter = 0
    print('Find output in find_clusters.log')
    fh = open('find_clusters.log', 'w')
    for file in run_threads(nthread, files, num_sp, semicon) :
        if file is None :
            continue
        fh.write('%s\n' %file)
        counter += 1
    fh.close()
    print ('Total: %d' %counter)
    return 0

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('num_th', help='Number of threads.', type=int)
    parser.add_argument('num_sp', help='Number of species.', type=int)
    parser.add_argument('-s', help='Find semiconserved clusters', action='store_true', default=False)
    args = parser.parse_args()
    main(args.num_sp, args.num_th, args.s)
    print('Done.')
