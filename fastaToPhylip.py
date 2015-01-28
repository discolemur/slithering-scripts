#! /usr/bin/env python

import os
import sys
from Bio import SeqIO

# This adds the "I" character to the first line of the phylip file. This make yn00 work.
# Also, we need to remove the stop codon.
# The number format for the phylip header is #taxa #bp
def prep_phylip_for_yn00(tmp, outfile) :
    ifh = open(tmp, 'r')
    ofh = open(outfile, 'w')
    first = True
    for line in ifh :
        if first :
            first = False
            num_sp = int(line.split()[0])
            num_bp = int(line.split()[1])
            line = line.strip() + " I\n"
        ofh.write(line)
    ofh.close()
    ifh.close()

def validate_headers(file) :
    headers = set()
    fh = open(file,'r')
    for line in fh :
        if line[0] == '>' :
            header = line[1:11]
            if header in headers :
                return False
            headers.add(header)
    fh.close()
    return True

def truncate_header(header) :
    if 'R_EP' in header :
        header = header.replace('R_', '')
    header = header.replace('_', '')
    return header[:10]

def fix_headers(old_file, new_file) :
    print('I\'ll remove the R_ from "R_EP00\d" headers.')
    ifh = open(old_file, 'r')
    ofh = open(new_file, 'w')
    for line in ifh :
        line = line.strip()
        if line[0] == '>' :
            line = line[1:].split('_assembly')[0]
            line = truncate_header(line)
            ofh.write('>')
        ofh.write('%s\n' %line)
    ofh.close()
    ifh.close()

def main(args) :
    if (len(args) != 3) :
        print("Gimme an input and output file next time.\n")
        print("Usage: %s <input.fasta> <output.phy>\n" %args[0])
        return 1
    infile = args[1]
    outfile = args[2]
    mod = False
    if not validate_headers(args[1]) :
        print('There will be duplicate headers with this file, so we will make a temporary file.')
        infile = '%s.mod.tmp' %args[1]
        fix_headers(args[1], infile)
        mod = True
    tmp = "tmp"
    SeqIO.convert(infile, "fasta", tmp, "phylip")
    if mod :
        os.remove(infile)
    prep_phylip_for_yn00(tmp, args[2])
    os.remove(tmp)

if __name__ == "__main__" :
    main(sys.argv)

