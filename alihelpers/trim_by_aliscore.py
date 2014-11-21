#! /usr/bin/env python

from argparse import ArgumentParser

def read_aliscore(infile) :
    alifile = '%s_List_random.txt' %infile
    fh = open(alifile, 'r')
    ali = []
    for line in fh :
        ali.extend([ int(x) for x in line.strip().split() ])
    return ali

def trim_seq(seq, ali) :
    seq = list(seq)
    for pos in ali :
        del seq[pos]
    return ''.join(seq)

def trim_fasta(infile, outfile, ali) :
    ali = sorted(ali, reverse=True)
    ifh = open(infile, 'r')
    ofh = open(outfile, 'w')
    seq = ''
    for line in ifh :
        line = line.strip()
        if line[0] == '>' :
            if seq != '' :
                seq = trim_seq(seq, ali)
                ofh.write('%s\n' %seq)
            ofh.write('%s\n' %(line))
            seq = ''
        else :
            seq += line
    if seq != '' :
        seq = trim_seq(seq, ali)
        ofh.write('%s\n' %seq)
    ofh.close()
    ifh.close()


def main(infile) :
    ali = read_aliscore(infile)
    outfile = '%s.trimmed.aln'  %'.'.join(infile.split('.')[:-1])
    trim_fasta(infile, outfile, ali)

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('infile', help='Fasta file (we will look for aliscore output file_List_random.txt)')
    args = parser.parse_args()
    main(args.infile)
