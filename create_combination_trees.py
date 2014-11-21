#! /usr/bin/env python

from argparse import ArgumentParser as AP
import os
import subprocess

# >1174.R_EP_006_assembly.comp8861_c0_seq3_456_3923_+.1

nowhere = None

class Gene(object) :
    def __init__(self, h, s) :
        self.header = h
        self.seq = s

class Cluster(object) :
    def __init__(self) :
        self.sp_to_genes = {}

    def add(self, header, seq) :
        sp = header
        if sp not in self.sp_to_genes :
            self.sp_to_genes[sp] = []
        self.sp_to_genes[sp].append(Gene(header, seq))

    def printall(self) :
        for sp in self.sp_to_genes :
            for gene in self.sp_to_genes[sp] :
                print('%s\t%s\t%d' %(sp, gene.header, len(gene.seq)))

    def _write_combo(self, genes, outfile) :
        fh = open(outfile, 'w')
        for gene in genes :
            fh.write('%s\n%s\n' %(gene.header, gene.seq))
        fh.close()

    def _align_combo(self, outfile) :
        global nowhere
        new_name = '%s.aln' %outfile.split('.')[0]
        subprocess.call("mafft %s > %s" %(outfile, new_name), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
        os.remove(outfile)

    def _combos_recurse(self, species, genes) :
        if len(species) == 0 :
            outfile = 'combo%d.fasta' %self.combo_counter
            print(outfile)
            self.combo_counter += 1
            self._write_combo(genes, outfile)
            self._align_combo(outfile)
            return
        for gene in self.sp_to_genes[species[0]] :
            genes.append(gene)
            self._combos_recurse(species[1:], genes)
            genes.pop(-1)

    def write_combinations(self) :
        self.combo_counter = 1
        species = list(self.sp_to_genes.keys())
        self._combos_recurse(species, [])

def read_file(infile) :
    fh = open(infile, 'r')
    cluster = Cluster()
    header = ''
    seq = ''
    for line in fh :
        line = line.strip()
        if line[0] == '>' :
            if header != '' :
                cluster.add(header, seq)
            header = line
            seq = ''
        else :
            seq += line
    if header != '' :
        cluster.add(header, seq)
    fh.close()
    return cluster

def main(infile) :
    cluster = read_file(infile)
    cluster.write_combinations()

if __name__=='__main__' :
    nowhere = open(os.devnull, 'w')
    parser = AP()
    parser.add_argument('cluster', metavar='cluster.fasta')
    args = parser.parse_args()
    main(args.cluster)
    nowhere.close()
