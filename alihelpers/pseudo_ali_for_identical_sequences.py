#! /usr/bin/env python

import glob
import os

def read_fasta(infile) :
    ''' Returns a dictionary in this schema -- {header(string)} -> sequence(string)
    Parameters :
        infile : string
    '''
    fasta_map = {}
    header = ''
    fh = open(infile, 'r')
    line_counter = 0
    seq_counter = 0
    for line in fh :
        line = line.strip()
        line_counter += 1
        if line[0] == '>' :
            seq_counter += 1
            header = line
            if header not in fasta_map :
                fasta_map[header] = ''
        else :
            fasta_map[header] += line.upper()
    fh.close()
    if line_counter > 0 and seq_counter == 0 :
        print('I think this isn\'t in fasta format. I\'m giving up.')
        exit(1)
    return fasta_map

def check_file(batch) :
    infile = batch.replace('Batch.sh','')
    fasta = read_fasta(infile)
    if len(fasta.values()) == 0 :
        print('%s is blank. It will be cleaned up.' %infile)
        os.remove(infile)
        os.remove(batch)
        return
    seq = list(fasta.values())[0]
    for header in fasta :
        if fasta[header] != seq :
            return
    os.remove(batch)
    listfile = '%s_List_random.txt' %infile
    fh = open(listfile, 'w')
    fh.close()
    

if __name__ == '__main__' :
    print('All files with *Batch.sh will be checked for identical sequences.')
    files = glob.glob('*Batch.sh')
    for file in files :
        check_file(file)
