#! /usr/bin/env python

import sys
import os
import subprocess
import timeit
import argparse

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
# Algorithm:
#    For each fasta file
#        For each gene in fasta file
#            For cluster in clusters
#                if gene in cluster : save to cluster
#######################################################

timing = False
start = timeit.default_timer()

num_organisms = 0
multiparanoid = ''
dir_name = ''

def checkpoint_time() :
    global timing
    global start
    if timing :
        checkpoint = timeit.default_timer()
        print('Time so far: %d' %(checkpoint - start))

class Cluster(object) :
# genes  ===   map from organism to map from gene-id to seq
    def __init__(self) :
        self.genes = {}
    
    def get_bin(self) :
        return len(self.genes)

    def add_gene(self, organism, id) :
        if organism not in self.genes :
            self.genes[organism] = {}
        self.genes[organism][id] = ""

    def get_all_names_sorted(self) :
        return sorted(self.genes.keys())

    def print_all(self) :
        for key in self.genes :
            print ('organism: %s' %key)
            print ('genes:')
            print (self.genes[key])

    def contains(self, organism, id) :
        if organism in self.genes :
            if id in self.genes[organism] :
                return True
        return False

    def set_sequence(self, organism, gene_id, seq) :
        self.genes[organism][gene_id] = seq

    def save(self, out_file, counter) :
        for organism in self.genes :
            for id in self.genes[organism] :
                seq = self.genes[organism][id]
                if len(seq) == 0 :
                    return
                id = id.replace(':', '_')
                id = id.replace('(', '_')
                id = id.replace(')', '_')
                out_file.write('>%d_%s_%s\n' %(counter, organism, id))
                out_file.write(seq)
                out_file.write('\n')

def add_cluster(clusters, cluster, num_organisms) :
    bin = cluster.get_bin()
    if bin in clusters :
        clusters[bin].append(cluster)
    else :
        clusters[bin] = [cluster]
    return clusters

# Input format:
# cluster    organism.pep    gene
# Assumes num_organisms is an int
def read_multiparanoid() :
    global multiparanoid
    global num_organisms
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
        cluster.add_gene(organism, id)
    in_file.close()
    if 0 in clusters :
        del clusters[0]
    for bin in clusters :
        print ('There are %d clusters in bin %d' %(len(clusters[bin]), bin))
    return clusters

def give_gene_to_cluster(clusters, organism, id, seq) :
    if id == '' or seq == '' :
        return clusters
    for key in clusters :
        for cluster in clusters[key] :
            if cluster.contains(organism, id) :
                cluster.set_sequence(organism, id, seq)
                return clusters
    return clusters

def get_gene_id(line) :
    id = ''
    line = line.strip()
    # Remove '>'
    line = line[1:]
    line = line.split(' ')
    if line[0] == '' :
        line = line[1:]
    # Handle simple case and normal fasta format case
    if len(line) == 1:
        id = line[0]
    # Handle complex case for transdecoder headers
    else :
        id = line[-1].split(' ')[-1]
    return id

def read_fastas(clusters, all_names) :
    for name in all_names :
        filename = name + '.pep'
        print('Reading %s...' %filename)
        in_file = open(filename, 'r')
        id = ''
        seq = ''
        for line in in_file :
            if line[0] == '>' :
                # Use previous gene
                if seq == '' and id != '' :
                    print ('Error: did not get gene sequence for id %s' %id)
                clusters = give_gene_to_cluster(clusters, name, id, seq)
                # Prepare to get new gene
                id = get_gene_id(line)
                if id == '' :
                    print ('Error: did not parse gene id from %s' %line)
                seq = ''
            else :
                seq = seq + line
        in_file.close()
    return clusters

def write_cluster(cluster, all_names, counter) :
    global dir_name
#    print ('Writing cluster %d' %counter)
    filename = "%s/tmp_%d_%d" %(dir_name, counter, cluster.get_bin())
    out_file = open(filename, 'w')
    cluster.save(out_file, counter)
    out_file.close()
#    checkpoint_time()
#    print ('Running mafft ...')
    # this is to silence mafft
    nowhere = open(os.devnull, 'w')
    subprocess.call("mafft %s > %s/cluster%d_bin%d.aln" %(filename, dir_name, counter, cluster.get_bin()), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
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

def writeOutput(clusters, all_names, total) :
    mkdirs()
    counter = 1
    percent = total / 10
    if percent == 0 :
        percent = 1
    # Write aligned clusters
    for bin in clusters :
        for cluster in clusters[bin] :
            if counter % percent == 0 :
                print ("Progress: %.2f%%" %(counter * 100.0 / total))
            write_cluster(cluster, all_names, counter)
            counter += 1

def handleArgs() :
    global num_organisms
    global multiparanoid
    global dir_name
    parser = argparse.ArgumentParser()
    parser.add_argument('organism_count', help='The number of organisms. Must be greater than 2.', type=int)
    parser.add_argument('input', help='Provide a location to solution.disco or a multiparanoid output file.')
    args = parser.parse_args()
    multiparanoid = args.input
    num_organisms = args.organism_count
    dir_name = "pep_all_%s" %multiparanoid.split('.')[0]
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
    clusters = read_fastas(clusters, all_names)
    # time
    checkpoint_time()
    writeOutput(clusters, all_names, getNumClusters(clusters))
    # time
    checkpoint_time()

if __name__ == "__main__" :
    main()

