#! /usr/bin/env python

from argparse import ArgumentParser
import glob
import numpy

'''
This script finds pairwise distances between sequences (fasta format) using the a simple jukes_cantor scoring matrix with indel penalty of 1.
'''

seqtype = None
indel_penalty = 1

jukes_cantor = '''
   A  G  C  T  N
A  2  0 -2 -2  0
G  0  2 -2 -2  0
C -2 -2  2  0  0
T -2 -2  0  2  0
N  0  0  0  0  0
'''

blosum62 = '''
   A  R  N  D  C  Q  E  G  H  I  L  K  M  F  P  S  T  W  Y  V  B  Z  X  *
A  4 -1 -2 -2  0 -1 -1  0 -2 -1 -1 -1 -1 -2 -1  1  0 -3 -2  0 -2 -1  0 -4 
R -1  5  0 -2 -3  1  0 -2  0 -3 -2  2 -1 -3 -2 -1 -1 -3 -2 -3 -1  0 -1 -4 
N -2  0  6  1 -3  0  0  0  1 -3 -3  0 -2 -3 -2  1  0 -4 -2 -3  3  0 -1 -4 
D -2 -2  1  6 -3  0  2 -1 -1 -3 -4 -1 -3 -3 -1  0 -1 -4 -3 -3  4  1 -1 -4 
C  0 -3 -3 -3  9 -3 -4 -3 -3 -1 -1 -3 -1 -2 -3 -1 -1 -2 -2 -1 -3 -3 -2 -4 
Q -1  1  0  0 -3  5  2 -2  0 -3 -2  1  0 -3 -1  0 -1 -2 -1 -2  0  3 -1 -4 
E -1  0  0  2 -4  2  5 -2  0 -3 -3  1 -2 -3 -1  0 -1 -3 -2 -2  1  4 -1 -4 
G  0 -2  0 -1 -3 -2 -2  6 -2 -4 -4 -2 -3 -3 -2  0 -2 -2 -3 -3 -1 -2 -1 -4 
H -2  0  1 -1 -3  0  0 -2  8 -3 -3 -1 -2 -1 -2 -1 -2 -2  2 -3  0  0 -1 -4 
I -1 -3 -3 -3 -1 -3 -3 -4 -3  4  2 -3  1  0 -3 -2 -1 -3 -1  3 -3 -3 -1 -4 
L -1 -2 -3 -4 -1 -2 -3 -4 -3  2  4 -2  2  0 -3 -2 -1 -2 -1  1 -4 -3 -1 -4 
K -1  2  0 -1 -3  1  1 -2 -1 -3 -2  5 -1 -3 -1  0 -1 -3 -2 -2  0  1 -1 -4 
M -1 -1 -2 -3 -1  0 -2 -3 -2  1  2 -1  5  0 -2 -1 -1 -1 -1  1 -3 -1 -1 -4 
F -2 -3 -3 -3 -2 -3 -3 -3 -1  0  0 -3  0  6 -4 -2 -2  1  3 -1 -3 -3 -1 -4 
P -1 -2 -2 -1 -3 -1 -1 -2 -2 -3 -3 -1 -2 -4  7 -1 -1 -4 -3 -2 -2 -1 -2 -4 
S  1 -1  1  0 -1  0  0  0 -1 -2 -2  0 -1 -2 -1  4  1 -3 -2 -2  0  0  0 -4 
T  0 -1  0 -1 -1 -1 -1 -2 -2 -1 -1 -1 -1 -2 -1  1  5 -2 -2  0 -1 -1  0 -4 
W -3 -3 -4 -4 -2 -2 -3 -2 -2 -3 -2 -3 -1  1 -4 -3 -2 11  2 -3 -4 -3 -2 -4 
Y -2 -2 -2 -3 -2 -1 -2 -3  2 -1 -1 -2 -1  3 -3 -2 -2  2  7 -1 -3 -2 -1 -4 
V  0 -3 -3 -3 -1 -2 -2 -3 -3  3  1 -2  1 -1 -2 -2  0 -3 -1  4 -3 -2 -1 -4 
B -2 -1  3  4 -3  0  1 -1  0 -3 -4  0 -3 -3 -2  0 -1 -4 -3 -3  4  1 -1 -4 
Z -1  0  0  1 -3  3  4 -2  0 -3 -3  1 -1 -3 -1  0 -1 -3 -2 -2  1  4 -1 -4 
X  0 -1 -1 -1 -2 -1 -1 -1 -1 -1 -1 -1 -1 -1 -2  0  0 -2 -1 -1 -1 -1 -1 -4 
* -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4  1
'''

def get_matrix(text_matrix) :
    '''
    Loads the matrix text into an easy-to-use dictionary.
    '''
    lines = [ line.strip() for line in text_matrix.split('\n') if line.strip() != '']
    heads = lines[0].split()
    lines = lines[1:]
    bmap = {}
    for line in lines :
        line = line.strip().upper().split()
        if line == '' :
            continue
        ch = line[0]
        bmap[ch] = {}
        line = [int(x) for x in line[1:]]
        for i in range(len(line)) :
            bmap[ch][heads[i]] = line[i]
    return bmap

def read_fasta(infile) :
    ''' Returns a dictionary in this schema -- {header(string)} -> sequence(string)
    Parameters :
        infile : string
    '''
    fasta_map = {}
    header = ''
    fh = open(infile, 'r')
    for line in fh :
        line = line.strip()
        if line[0] == '>' :
            header = line[1:]
            if header not in fasta_map :
                fasta_map[header] = ''
            else :
                print('ERROR: duplicate headers')
                exit(1)
        else :
            fasta_map[header] += line.upper()
    fh.close()
    return fasta_map, len(fasta_map[header])

def get_score(seq1, seq2) :
    global score_matrix
    global indel_penalty
    score = 0
    for i in range(len(seq1)) :
        if seq1[i] == '-' or seq2[i] == '-' :
            score += indel_penalty
        else :
            score += score_matrix[seq1[i]][seq2[i]]
    return score

def get_scores(fasta) :
    '''
    Returns a dict of dict : {header1} -> {header2} -> score(int)
    '''
    all_scores = []
    scores = {}
    headers = list(fasta.keys())
    for i in range(0, len(headers)) :
        header1 = headers[i]
        scores[header1] = {}
        for j in range(i+1, len(headers)) :
            header2 = headers[j]
            scores[header1][header2] = get_score(fasta[header1], fasta[header2])
            all_scores.append(scores[header1][header2])
    return scores, numpy.mean(all_scores)

def get_percent_variation(fasta) :
    headers = list(fasta.keys())
    total = len(fasta[headers[0]])
    num_diff = 0
    for i in range(len(fasta[headers[0]])) :
        bp = fasta[headers[0]][i]
        same = True
        for j in range(1, len(headers)) :
            if fasta[headers[j]][i] != bp :
                same = False
        if not same :
            num_diff += 1
    percent_variation = (num_diff * 100.0) / total
    return percent_variation

def trim(fasta, i) :
    for key in fasta :
        del fasta[key][i]
    return fasta

def trim_fasta(fasta) :
    headers = list(fasta.keys())
    # Convert seqs to lists
    for header in headers :
        fasta[header] = list(fasta[header])
    size = len(fasta[headers[0]])
    half = len(headers) / 2
    # Trim front.
    for i in range(size) :
        counter = 0
        for header in headers :
            if fasta[header][i] == '-' :
                counter += 1
        if counter > half :
            fasta = trim(fasta, i)
        else :
            break
    # Trim back.
    size = len(fasta[headers[0]])
    for i in range(size) :
        pos = 0 - i
        counter = 0
        for header in headers :
            if fasta[header][pos] == '-' :
                counter += 1
        if counter > half :
            fasta = trim(fasta, pos)
        else :
            break
    # Convert seqs back to strings
    for header in headers :
        fasta[header] = ''.join(fasta[header])
    return fasta , len(list(fasta.values())[0])

def handle_file(infile) :
    global seqtype
    global score_matrix
    fasta, length = read_fasta(infile)
    if seqtype is None :
        if len(set(list(fasta.values())[0])) < 6 :
            seqtype = 'nuc'
            score_matrix = get_matrix(jukes_cantor)
        else :
            seqtype = 'pep'
            score_matrix = get_matrix(blosum62)
    fasta, new_length = trim_fasta(fasta)
#    if new_length != length :
#        print('Trimmed %d' %(length - new_length))
    length = new_length
    percent_variation = get_percent_variation(fasta)
    scores, mean_dist = get_scores(fasta)
    return length, scores, percent_variation, mean_dist

'''
headers :
1 2 3 4 5

report :
 1 2 3 4
5
4
3
2
'''
# TODO
#def report_scores(scores) :
#    for header1 in scores :
#        for header2 in scores[header1] :
#            print('%s\t%d' %(header1, scores[header1][header2]))

def report_all(infile, length, percent_variation, mean_dist, scores) :
    print(infile)
    print('Length:\t%d' %length)
    print('Percent variation:\t%.2f%%' %percent_variation)
    print('Mean pairwise score (normalized):\t%f' %(mean_dist/length))
    #report_scores(scores)

def main(infile) :
    global seqtype
    if infile != '' :
        length, scores, percent_variation, mean_dist = handle_file(infile)
        if length > 300 and percent_variation < 32 :
            report_all(infile, length, percent_variation, mean_dist, scores)
        return 0
    files = glob.glob('*.aln')
    for file in files :
        length, scores, percent_variation, mean_dist = handle_file(file)
        if seqtype == 'pep' and length > 100 and percent_variation < 10 :
            report_all(file, length, percent_variation, mean_dist, scores)
        elif seqtype == 'nuc' and length > 300 and percent_variation < 30 :
            report_all(file, length, percent_variation, mean_dist, scores)


score_matrix = {}
if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('-infile', default = '')
    args = parser.parse_args()
    main(args.infile) 

