#! /usr/bin/env python

#Calculate N50 statistic

from sys import argv
from math import floor
import glob

files = glob.glob('*.Trinity.fasta')

if len(files) == 0 :
    print('Could not find *.Trinity.fasta files to analyze.')
    exit(1)

def get_data(infile) :
    '''
        To be fair, much of this function was written by my supervisor: Anton Suvorov.
    '''
    ifh = open(infile)

    fasta_dic={}

    nucleotides = {'A':0, 'T':0, 'C':0, 'G':0}
    total = 0.0

    header = ''

    for line in ifh:
        line = line.strip()
        if line[0]==">" :
            header=line[1:]
            fasta_dic[header]=""
        else:
            for char in line :
                nucleotides[char] += 1
                total += 1
            fasta_dic[header]+=line
    ifh.close()

    vector=[]
    vector1=[]
    for e in fasta_dic.values():
        vector1+=[len(e)]
        mult=[len(e)]*len(e)
        vector+=mult

    vector=sorted(vector)
    text_file = open("L_distr.%s.txt" %infile, "w")
    text_file.write(str(vector1))
    text_file.close()
    max_len=max(vector)
    min_len=min(vector)
    ncont=len(fasta_dic)

    if len(vector)%2==0:
        N50=(vector[int(len(vector)/2)]+vector[int(len(vector)/2)-1])/2
    else:
        N50=vector[int(floor(len(vector)/2))]

    pA, pT, pG, pC = nucleotides['A']/total, nucleotides['T']/total, nucleotides['G']/total, nucleotides['C']/total
    print('%s\t%f\t%d\t%d\t%d\t%f\t%f\t%f\t%f' %(file, N50, max_len, min_len, ncont, pA, pT, pG, pC))


print('Assembly\tN50\tMaxContig\tMinContig\tNContigs\tA\tT\tG\tC')
for file in files :
    get_data(file)

