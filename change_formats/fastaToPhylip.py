#! /usr/bin/env python

import os
import shutil
import sys
from Bio import SeqIO

# Converts fasta to Phylip, and prepares phylip to work with paml package (there are some stupid requirements)


# This make yn00 work.
# Because the phylip file is in Interleaved format, add 'I' to the first line.
# The number format for the phylip header is #taxa #bp
def prep_phylip_for_yn00(tmp, outfile) :
    ifh = open(tmp, 'r')
    ofh = open(outfile, 'w')
    first = True
    num_names = 0
    for line in ifh :
        if first :
            first = False
            num_sp = int(line.split()[0])
            num_bp = int(line.split()[1])
            line = line.strip() + " I\n\n"
        elif (not first) and (num_names != num_sp) and (len(line.strip()) != 0) :
            line = line.strip()
            line = line.split()
            tmp = line[0] + '  '
            tmp += ' '.join(line[1:])
            line = tmp + '\n'
            num_names += 1
        ofh.write(line)
    # Maybe need extra line?
    ofh.write('\n')
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

# Also, we need to remove the stop codon.
def fix_headers(old_file) :
    new_file = 'BOGUS'
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
    shutil.move(new_file, old_file)

# Must remove stop codons, including before '-' characters, to handle indels. They may not all stop at the end of the alignment.
def remove_stop_codons(seq) :
    stop_codons = ['TAG','TAA','TGA']
    nucs = 0
    seq = list(seq)
    codon = ''
    places = []
    for i in range(1, len(seq) + 1) :
        # Look backwards
        pos = 0 - i
        if nucs == 3 :
            break
        if seq[pos] != '-' :
            codon = seq[pos] + codon
            places.append(pos)
            nucs += 1
    # places is sorted , least negative to most negative
    if codon.upper() in stop_codons :
        size = len(seq)
        # Remove locations, from back to front to keep from frame shift errors.
        for pos in places :
            del(seq[size + pos])
    return ''.join(seq)

def copy_to_tmp(infile, tmpfile) :
    fasta_map = {}
    ifh = open(infile, 'r')
    for line in ifh :
        line = line.strip()
        if line[0] == '>' :
            header = line
            fasta_map[header] = ''
        else :
            fasta_map[header] += line
    ifh.close()
    ofh = open(tmpfile, 'w')
    for header in fasta_map :
        seq = fasta_map[header]
        # Remove the stop codon.
        seq = remove_stop_codons(seq)
        ofh.write('%s\n%s\n' %(header, seq))
    ofh.close()

def main(args) :
    if (len(args) != 3) :
        print("Gimme an input and output file next time.\n")
        print("Usage: %s <input.fasta> <output.phy>\n" %args[0])
        return 1
    infile = args[1]
    tmpfile = '%s.mod.tmp' %args[1]
    copy_to_tmp(infile, tmpfile)
    outfile = args[2]
    mod = False
    if not validate_headers(args[1]) :
        print('Headers will change in phylip format.')
        fix_headers(tmpfile)
        mod = True
    tmpphylip = "tmpphylip"
    SeqIO.convert(tmpfile, "fasta", tmpphylip, "phylip")
    prep_phylip_for_yn00(tmpphylip, outfile)
    os.remove(tmpfile)
    os.remove(tmpphylip)

if __name__ == "__main__" :
    main(sys.argv)

