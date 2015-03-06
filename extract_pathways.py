#! /usr/bin/env python

import glob
from argparse import ArgumentParser

'''
Useful info about the blast input format:

array position     field
0     query name
1     subject name
2     percent identities
3     aligned length
4     number of mismatched positions
5     number of gap positions
6     query sequence start
7     query sequence end
8     subject sequence start
9     subject sequence end
10     e-value
11     bit score

Example:
cds.c13004_g1_i1|m.14133        dme:Dmel_CG2621 30.91   110     69      4       1       105     265     372     4e-12   52.8


METHOD:
We will take the best "percent identities" hit for each droso gene (if tied, lowest e-value of those two).

OUTPUT:
We will make a file for each species with its full pathway.
We will make a file for each gene, clustering orthologies together.
'''

def read_blast(infile) :
    '''
    Returns : {droso_gene} -> [taxon_gene, percent_identity, e-value]
    '''
    fh = open(infile, 'r')
    best_hits = {}
    for line in fh :
        line = line.strip().split('\t')
        if line[0][:4] == 'cds.' :
            line[0] = line[0][4:]
        if line[1][:4] == 'dme:' :
            line[1] = line[1][4:]
        if line[1] not in best_hits :
            best_hits[line[1]] = [line[0], float(line[2]), float(line[10])]
            continue
        # Condition that line is better than best so far.
        elif ( best_hits[line[1]][1] < float(line[2]) ) or ( best_hits[line[1]][1] == float(line[2]) and best_hits[line[1]][2] > float(line[10] ) ) :
            best_hits[line[1]] = [line[0], float(line[2]), float(line[10])]
    fh.close()
    return best_hits

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
            header = line[1:].split(' ')[0]
            if header not in fasta_map :
                fasta_map[header] = ''
            else :
                print('ERROR: duplicate ids exist in this fasta file.\n%s' %header)
        else :
            fasta_map[header] += line
    fh.close()
    return fasta_map

def write_pathway(taxon, best_hits_taxon, pathway_name) :
    outfile = '%s.%s.fasta' %(taxon, pathway_name)
    filestub = '%s.cds.fasta' %taxon
    fasta_file = '/fslgroup/fslg_BybeeLab/compute/all_illumina_trinity_transcriptomes/inparanoid_computations/fasta_extracted/%s' %filestub
    fasta_map = read_fasta(fasta_file)
    fh = open(outfile, 'w')
    for gene in best_hits_taxon :
        header = '>%s %s' %(best_hits_taxon[gene][0], gene)
        seq = fasta_map[best_hits_taxon[gene][0]]
        best_hits_taxon[gene].append(seq)
        fh.write('%s\n%s\n' %(header, seq))
    fh.close()
    return best_hits_taxon

def write_orthologies(best_hits, gene, pathway_name) :
    outfile = '%s.%s.fasta' %(gene, pathway_name)
    fh = open(outfile, 'w')
    for taxon in best_hits :
        if gene in best_hits[taxon] :
            header = '>%s %s' %(best_hits[taxon][gene][0], gene)
            seq = best_hits[taxon][gene][-1]
            fh.write('%s\n%s\n' %(header, seq))
    fh.close()

def main(pathway_name) :
    blast_files = glob.glob('*.hits')
    # {taxon} -> {droso_gene} -> [taxon_gene, percent_identity, e-value]
    best_hits = {}
    taxon = ''
    for blast_file in blast_files :
        taxon = blast_file.split('.')[0]
        print('Handling %s' %taxon)
        best_hits[taxon] = read_blast(blast_file)
        best_hits[taxon] = write_pathway(taxon, best_hits[taxon], pathway_name)
    for gene in best_hits[taxon].keys() :
        write_orthologies(best_hits, gene, pathway_name)

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('pathway_name', help='The name of the pathway, for output file purposes.')
    args = parser.parse_args()
    main(args.pathway_name)

