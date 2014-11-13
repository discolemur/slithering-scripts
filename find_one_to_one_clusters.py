#! /usr/bin/env python

from argparse import ArgumentParser
import glob

def get_sp(line, source) :
    if source == 'hamstr' :
        return line.split('|')[2]
    if '|' in line :
        sp = line.split('|')[1]
    elif '_' in line :
        sp = line.split('_')[1]
    else :
        print('Couldn\'t parse the species, sorry.')
    return sp

def is_one_to_one(infile, num_sp, source) :
    result = True
    seqs = {}
    sp = ''
    for line in open(infile, 'r'):
        if line[0] == '>' :
            sp = get_sp(line, source)
            if sp in seqs :
                result = False
                break
            seqs[sp] = ''
        else:
            seqs[sp] += line[:-1].replace('-','')
    if len(list(seqs.keys())) != num_sp :
        result = False
    for sp in seqs :
        if len(seqs[sp]) == 0 :
            result = FalseA
    return result

def get_one_to_ones(files, num_sp, source) :
    for file in files :
        if is_one_to_one(file, num_sp, source) :
            yield file
 
def main(num_sp, source) :
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
    for file in get_one_to_ones(files, num_sp, source) :
            print(file)
            counter += 1
    print ('Total: %d' %counter)
    return 0

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('source', help='Source of clusters (lets us know how to parse the headers) (options: hamstr, other)')
    parser.add_argument('num_sp', help='Number of species.', type=int)
    args = parser.parse_args()
    main(args.num_sp, args.source)

print('Done.')
