#! /usr/bin/env python

import sys
import os
import subprocess
import timeit
import argparse
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import parallelize

# Please only give me files from transdecoder. This means .pep (for proteins) and .cds (for dna).

def info() :
    print ('\nSpecies have only unique genes, no paralogy')
    print ('Missing species are filled in with dashes after alignment')
    print ('Clusters have a bin number for how many organisms are present in each cluster')
    print ('')
    print ('This script')
    print ('Takes disco solution to multiparanoid')
    print ('And associated fasta files and')
    print ('Produces clusters (conserved, semiconserved, or complete (allowing paralogy) )')
    print ('')
    print ('Assume the following about filenames:')
    print ('\tIf the peptide files have format filename.pep')
    print ('\tThen the DNA files have format filename.fasta')
    print ('')
    print ('Assume DNA/AA fasta files are located in the current directory\n')

#######################################################
# Method:
#    For each fasta file
#        For each gene in fasta file
#            For cluster in clusters
#                if gene in cluster : save to cluster
#######################################################

timing = False
start = timeit.default_timer()

num_organisms = 0
multiparanoid = ''
output_type = ''
dir_name = ''
threads = 1

def checkpoint_time() :
    global timing
    global start
    if timing :
        checkpoint = timeit.default_timer()
        print('Time so far: %d' %(checkpoint - start))

def change_header(line) :
    line = line.replace('|', '_')
    line = line.replace(':', '_')
    line = line.replace('(', '_')
    line = line.replace(')', '_')
    return line

class Cluster(object) :
# genes  ===   {organism} -> {id} -> sequence
    def __init__(self) :
        self.genes = {}

#    No paralogy and no missing organisms
    def is_conserved(self) :
        return (self.is_complete() and self.is_semiconserved())

#    No paralogy
    def is_semiconserved(self) :
        if len(list(self.genes.keys())) < 2 :
            return False
        for sp in self.genes :
            if len(list(self.genes[sp].keys())) != 1:
                return False
        return True

#    No missing organisms
    def is_complete(self) :
        if len(list(self.genes.keys())) != num_organisms :
            return False
        return True

    # Do not allow paralogs
    def is_valid(self, num_organisms) :
        if output_type == 'c' :
            return self.is_conserved()
        elif output_type == 'm' :
            return self.is_complete()
        elif output_type == 's' :
            return self.is_semiconserved()
        elif output_type == 'a' :
            return True
        else :
            print('Unknown output type. Tell Nick that there is a bug.')
            return False
        
    def get_bin(self) :
        return len(self.genes)

    def add_gene_id(self, organism, id) :
        if organism not in self.genes :
            self.genes[organism] = {}
        self.genes[organism][id] = ''

    def get_all_names_sorted(self) :
        return sorted(self.genes.keys())

    def print_all(self) :
        for key in self.genes :
            print ('organism: %s' %key)
            print ('genes:')
            print (self.genes[key])

    def save(self, out_file, counter) :
        if len(self.genes) == 0 :
            print ('ERROR! All sequences were lost in this cluster %d.' %counter)
            out_file.write('ERROR! All sequences were lost in this cluster %d.' %counter)
            print(self.genes)
            return False
        for organism in self.genes :
            for id in self.genes[organism] :
                header = '>%d|%s|%s' %(counter, organism, id)
                header = change_header(header)
                out_file.write('%s\n' %header)
                seq = self.genes[organism][id]
                if seq == '' :
                    print('Oh no! Dead sequence for %s %s' %(organism, id))
                out_file.write(seq)
                out_file.write('\n')
        return True

def add_cluster(clusters, cluster, num_organisms) :
    if cluster.is_valid(num_organisms) :
        bin = cluster.get_bin()
        if bin in clusters :
            clusters[bin].append(cluster)
        else :
            clusters[bin] = [cluster]
    return clusters

# Input format:
# cluster    organism.pep    gene
# Assumes num_organisms is an int
# clusters = {bin} -> [Cluster]
def read_multiparanoid() :
    global multiparanoid
    global num_organisms
    global uses_dna
    print ('Reading input %s . . .' %multiparanoid)
    in_file = open(multiparanoid, 'r')
    clusters = {}
    i = 0
    cluster = Cluster()
    for line in in_file :
        line = line.strip()
        line = line.split('\t')
        # line is not for this cluster
        if not line[0].isdigit() :
            continue
        # line indicates a new cluster
        elif i != int(line[0]) :
            i = int(line[0])
            clusters = add_cluster(clusters, cluster, num_organisms)
            cluster = Cluster()
        # line goes in current cluster
        # remove the file extension
        organism = line[1].split('.')[0]
        id = line[2]
        cluster.add_gene_id(organism, id)
    in_file.close()
    if 0 in clusters :
        del clusters[0]
    for bin in clusters :
        print ('There are %d clusters in bin %d' %(len(clusters[bin]), bin))
    return clusters

# Example header:
# >cds.comp2848_c0_seq2|m.2015 comp2848_c0_seq2|g.2015  ORF comp2848_c0_seq2|g.2015 comp2848_c0_seq2|m.2015 type:complete len:342 (-) comp2848_c0_seq2:180-1205(-)

# Example disco id :
# comp4103_c0_seq1:108-1082(+)

def get_gene_id(line) :
    return line[1:].split(' ')[-1].strip()

# fastas = {name} -> {id} -> seq
def read_fastas(all_names) :
    global uses_dna
    fastas = {}
    for name in all_names :
        filename = name + '.pep'
        if uses_dna :
            filename = name + '.cds.fasta'
        print('Reading %s...' %filename)
        in_file = open(filename, 'r')
        fastas[name] = {}
        id = ''
        for line in in_file :
            line = line.strip()
            if line[0] == '>' :
                id = get_gene_id(line)
                fastas[name][id] = ''
            else :
                fastas[name][id] += line
        in_file.close()
    return fastas

# genes  ===   {organism} -> {id} -> sequence
def load_clusters(fastas, clusters) :
    for bin in clusters :
        for cluster in clusters[bin] :
            for name in cluster.genes :
                for id in cluster.genes[name] :
                    cluster.genes[name][id] = fastas[name][id]
    return clusters

# this is to silence mafft
nowhere = open(os.devnull, 'w')
def write_cluster(cluster, counter) :
    global dir_name
    global nowhere
#    print ('Writing cluster %d' %counter)
    filename = "%s/tmp_%d_%d" %(dir_name, counter, cluster.get_bin())
    out_file = open(filename, 'w')
    if not cluster.save(out_file, counter) :
        out_file.close()
        os.remove(filename)
        return
    out_file.close()
#    checkpoint_time()
#    print ('Running mafft ...')
    sys.stdout.write('.')
    subprocess.call("mafft %s > %s/cluster%d_bin%d.aln" %(filename, dir_name, counter, cluster.get_bin()), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
    #subprocess.call("mafft %s > %s/cluster%d_bin%d.aln" %(filename, dir_name, counter, cluster.get_bin()), shell=True)
    os.remove(filename)
    checkpoint_time()

def mkdirs() :
    global dir_name
    if not os.path.exists(dir_name) :
        os.makedirs(dir_name)

def getAllNames(clusters) :
    # Assume there is a cluster containing all the organisms
    # Look in bin given by number of organisms
    big_cluster = clusters[num_organisms][0]
    all_names = big_cluster.get_all_names_sorted()
    return all_names


def getNumClusters(clusters) :
    total = 0
    for bin in clusters :
        total += len(clusters[bin])
    print ('There are %d clusters in total.' %total )
    return total

def writeOutput(clusters, total) :
    mkdirs()
    counter = 1
    percent = total / 10
    if percent == 0 :
        percent = 1
    # Write aligned clusters
    for bin in clusters :
        print('Handling bin %d' %bin)
        for cluster in clusters[bin] :
            if counter % percent == 0 :
                print ("Progress: %.2f%%" %(counter * 100.0 / total))
            write_cluster(cluster, counter)
            counter += 1

def write_batch(clusters, counter) :
    for cluster in clusters :
        write_cluster(cluster, counter)
        counter += 1

def writeOutputMultithread(clusters) :
    global threads
    all_clusters = []
    keys = clusters.keys()
    for bin in keys :
        all_clusters.extend(clusters[bin])
        del clusters[bin]
    mkdirs()
    total = len(all_clusters)
    print('There are %d clusters in total.' %total)
    # Write aligned clusters
    parallelize(all_clusters, write_batch, threads)

def determineOutputType() :
    global output_type
    global dir_name
    global output_type
    global multiparanoid
    global uses_dna
    multiparanoid_abrv = multiparanoid.split('.')[0]
    subscript = 'pep'
    if uses_dna :
        subscript = 'dna'
    if (output_type == 'm') :
        dir_name = "%s_complete_%s" %(subscript, multiparanoid_abrv)
        print('Running complete clustering (allows paralogs)')
    elif (output_type == 's') :
        dir_name = "%s_semiconserved_%s" %(subscript, multiparanoid_abrv)
        print('Running semiconserved clustering.')
    elif (output_type == 'c') :
        dir_name = "%s_conserved_%s" %(subscript, multiparanoid_abrv)
        print('Running conserved clustering.')
    elif (output_type == 'a') :
        dir_name = "%s_all_%s" %(subscript, multiparanoid_abrv)
        print('Oh, boy! You want ALL the clusters!')
    else :
        return False
    return True

def handleArgs() :
    global num_organisms
    global multiparanoid
    global uses_dna
    global output_type
    global threads
    parser = argparse.ArgumentParser()
    parser.add_argument('organism_count', help='The number of organisms. Must be greater than 2.', type=int)
    parser.add_argument('--uses_dna', help='Set this if you want to cluster based on dna (.fasta) sequences and not amino acid (.pep) sequences.', action='store_true')
    parser.add_argument('output_type', help='Options are c , s , m, and a for conserved, semiconserved, complete, all clusters (regardless of any abnormalitites) (respectively)')
    parser.add_argument('input', help='Provide a location to solution.disco or a multiparanoid output file.')
    parser.add_argument('-t', help='Number of threads. If specified, multithreading is enabled.', type=int, default=1)
    args = parser.parse_args()
    multiparanoid = args.input
    uses_dna = args.uses_dna
    output_type = args.output_type
    num_organisms = args.organism_count
    threads = args.t
    if threads < 1 :
        print('Invalid number of threads.')
        return False
    if not determineOutputType() :
        return False
    if num_organisms < 2 :
        return False
    if not os.path.isfile(multiparanoid) :
        print('Cannot locate multiparanoid file: %s' %multiparanoid)
        return False
    return True

def main() :
    global num_organisms
    global multiparanoid
    info()
    if not handleArgs() :
        return
    # Read multiparanoid
    clusters = read_multiparanoid()
    if len(clusters) == 0 :
        return
    all_names = getAllNames(clusters)
    # time
    checkpoint_time()
    # Read fasta files
    print ("Gathering clusters")
    fastas = read_fastas(all_names)
    clusters = load_clusters(fastas, clusters)
    # time
    checkpoint_time()
    if threads == 1 :
        writeOutput(clusters, getNumClusters(clusters))
    else :
        writeOutputMultithread(clusters)
    # time
    checkpoint_time()

if __name__ == "__main__" :
    main()

