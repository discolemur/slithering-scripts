#! /usr/bin/env python

from statistics import variance
from fractions import Fraction
import argparse
import glob
import math
import sys
import threading

def get_aliscore(alifile) :
    fh = open(alifile, 'r')
    result = 0
    for line in fh :
        line = line.strip()
        if line == '' :
            continue
        result += len(line.split(' '))
    fh.close()
    return result

AAcodes = {'W': 4, 'I': 4, 'E': 1, 'S': 2, 'D': 1, 'P': 3, 'Y': 4, 'F': 4, 'U': 3, 'V': 4, 'K': 1, 'M': 4, 'G': 3, 'N': 2, 'H': 1, 'R': 1, 'L': 4, 'Q': 2, 'T': 2, 'C': 3, 'A': 4}
code_to_class = {3:'AAspecial', 2:'AAuncharged_polar', 1:'AAcharged', 4:'AAhydrophobic'}

# Returns variance of proportions of types of amino acids
def get_amino_acid_stats(seqs) :
    global AAcodes
    stats = {1:[], 2:[], 3:[], 4:[]}
    count = 0
    for header in seqs.keys() :
        count += 1
        seqstats = {1:0,2:0,3:0,4:0}
        size = 0
        for aa in seqs[header] :
            if aa != '-' and aa in AAcodes :
                seqstats[AAcodes[aa]] += 1
                size += 1
        for i in range(1,5) :
            if size != 0 :
                stats[i].append(Fraction(seqstats[i], size))
            else :
                stats[i].append(0)
    charged = math.sqrt(variance(stats[1]))
    uncharged = math.sqrt(variance(stats[2]))
    special = math.sqrt(variance(stats[3]))
    hydrophobic = math.sqrt(variance(stats[4]))
    return special, uncharged, charged, hydrophobic

amino_acids = ['W', 'I', 'E', 'S', 'D', 'P', 'Y', 'F', 'U', 'V', 'K', 'M', 'G', 'N', 'H', 'R', 'L', 'Q', 'T', 'C', 'A']
def read_aln(seqfile) :
    global amino_acids
    lines = [line.strip() for line in open(seqfile,'r')]
    header = ''
    seqs = {}
    gaps = 0
    bases = 0
    longest = 0
    size_count = 0
    shortest = sys.maxsize
    for line in lines :
        if line[0] == '>' :
            if size_count > longest :
                longest = size_count
            elif size_count < shortest :
                shortest = size_count
            header = line
            seqs[header] = ''
            size_count = 0
        else :
            gaps += line.count('-')
            for aa in amino_acids :
                val = line.count(aa)
                bases += val
                size_count += val
            seqs[header] += line
    length = len(seqs[header])
    num_seqs = len(list(seqs.keys()))
    range = longest - shortest
    special, uncharged, charged, hydrophobic = get_amino_acid_stats(seqs)
    return [length, num_seqs, gaps, bases, range, charged, uncharged, special, hydrophobic]

def handle_files(files, homology, lines, begin) :
    print('Thread beginning at %d begun.' %begin)
    i = begin
    for alifile in files :
        seqfile = alifile.split('_List')[0]
        name = '%s' %(seqfile.split('/')[-1].split('.')[0])
        output_list = [name]
        aliscore = get_aliscore(alifile)
        output_list.append(str(aliscore))
        output_list.extend([str(x) for x in read_aln(seqfile)])
        output_list.append(homology)
        lines[i] = '%s\n' %'\t'.join(output_list)
        i += 1
        if i % 100 == 0 :
            print('100 Progress from %d !' %begin)
    print('Thread begun at %d finished' %begin)

def run_threads(num_threads, files, homology) :
    lines = [None for i in range(len(files))]
    threads = []
    div = int(len(files) / num_threads)
    begin = 0
    end = div + (len(files) % num_threads)
    for i in range(num_threads) :
        thread = threading.Thread(target=handle_files, args=(files[begin:end], homology, lines, begin))
        threads.append(thread)
        thread.start()
        begin = end
        end += div
    for thread in threads :
        thread.join()
    return lines

def main(dir, homology, output, num_threads) :
    files = glob.glob('%s/*List*' %dir)
    print('Found %d files' %len(files))
    lines = run_threads(num_threads, files, homology)
    ofhandle = open(output, 'w')
    ofhandle.write('id\taliscore\tlength\tnum_seqs\tnum_gap\tnum_aa\trange\tAAcharged\tAAuncharged\tAAspecial\tAAhydrophobic\tout\n')
    for line in lines :
        ofhandle.write(line)
    ofhandle.close()

if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='Number of threads.', type=int, default=1)
    parser.add_argument('-d', help='Directory containing aligned clusters with their *List* aliscore files.', default='.')
    parser.add_argument('homology', help='H = homologous, NH = non homologous, ? = unknown homology status')
    parser.add_argument('output', help='Output filename. Output will be a table of stuff, so probably you should use a .txt extention.')
    args = parser.parse_args()
    main(args.d, args.homology, args.output, args.t)

