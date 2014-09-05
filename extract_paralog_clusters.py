#! /bin/env python

import argparse
import os
import subprocess
import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update

# METHOD #
# Load disco into structure of clusters (orthologous)
# Load fasta files one by one (each fasta has map ID -> seq)
# Traverse the disco structure and pull sequences from fastas when paralogs are found for that organism
# Save paralogous clusters (same organism, same cluster, more than one sequence)
# (Put saved stuff inside dir, and subdir (see variables))

## GLOBALS ##

dir = 'paralogs'
organisms = set()
nowhere = open(os.devnull, 'w')

#############

class Cluster(object) :
	# Does python have inner classes? Yes.
	class Gene(object) :
		def __init__(self, organism, gene_id) :
			self.organism = organism
			self.id = gene_id

		def set_seq(self, sequence) :
			if sequence == '' :
				print('You are adding an empty sequence, FYI.')
			self.seq = sequence

	class Paralog(object) :
		def __init__(self, best_gene, paralog_gene) :
			self.best = best_gene
			self.paralog = paralog_gene

	def __init__(self, cluster_id) :
		self.id = cluster_id
		self.genes = {}

	# Genes is a map {organism} -> [list of genes]
	def add(self, organism, gene_id) :
		if organism not in self.genes :
			self.genes[organism] = []
		self.genes[organism].append(self.Gene(organism, gene_id))

	# This removes all organisms with one or zero genes
	def reduce(self) :
		for sp in list(self.genes.keys()) :
			if len(self.genes[sp]) <= 1 :
				del(self.genes[sp])

	def get_best_index(self, arr) :
		best_size = 0
		best_index = -1
		for i in range(0, len(arr)) :
			if len(arr[i].seq) > best_size :
				best_index = i
				best_size = len(arr[i].seq)
		return best_index

	def get_paralogs(self, fasta, organism) :
		result = []
		if organism in self.genes :
			for gene in self.genes[organism] :
				gene.set_seq(fasta[gene.id])
				del(fasta[gene.id])
			best = self.get_best_index(self.genes[organism])
			size = len(self.genes[organism])
			for i in range(0, size) :
				if best != i :
					result.append(self.Paralog(self.genes[organism][best], self.genes[organism][i]))
		return result

	def write_paralogs(self, fasta, organism, path) :
		# Find genes for this organism. If size is greater than one, write data.
		global nowhere
		paralogs = self.get_paralogs(fasta, organism)
		counter = 1
		for paralog in paralogs :
			filename = '%s/%s_%d.fa' %(path, self.id, counter)
			of_handle = open(filename, 'w')
			of_handle.write('>%s 1\n%s\n' %(paralog.best.id, paralog.best.seq))
			of_handle.write('>%s 0\n%s\n' %(paralog.paralog.id, paralog.paralog.seq))
			of_handle.close()
			new_name = filename[:-3] + '.aln'
			subprocess.call("mafft %s > %s" %(filename, new_name), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
			os.remove(filename)
			counter += 1
		return False

def write_clusters_for_organism(cluster_map, fasta, organism, path) :
	for id in cluster_map :
		cluster_map[id].write_paralogs(fasta, organism, path)

def parse_id(line) :
	return line[1:].strip().split(' ')[-1]

def get_seq_data(organism) :
	# org_map is seq_id -> seq
	# It just holds the fasta file in a query-able structure
	org_map = {}
	if_handle = open(organism, 'r')
	id = ''
	seq = ''
	for line in if_handle :
		if line[0] == '>' :
			if seq != '' and id != '' :
				org_map[id] = seq
			id = parse_id(line)
			seq = ''
		else :
			seq = seq + line.strip()
	if_handle.close()
	# Take care of last seq in the file
	org_map[id] = seq
	return org_map

def handle_organism(organism, cluster_map):
	global dir
	fasta = get_seq_data(organism)
	subdir = organism.split('.')[0]
	path = '%s/%s' %(dir, subdir)
	if not os.path.exists(path) :
		os.makedirs(path)
	write_clusters_for_organism(cluster_map, fasta, organism, path)

def write_clusters(cluster_map) :
	global organisms
	do_progress_update(organisms, handle_organism, cluster_map)
	
def add_line_to_map(line, doc) :
	global organisms
	line = line.strip().split('\t')
	cluster = line[0]
	organism = line[1]
	gene_id = line[2]
	if cluster not in doc :
		doc[cluster] = Cluster(cluster)
	doc[cluster].add(organism, gene_id)
	organisms.add(organism)
	return doc

# Disco format:
# cluster       organism        gene
#
# Resulting map fits this schema:
# {cluster id} -> Cluster objects
def gather_paralogs(filename) :
	doc = {}
	if_handle = open(filename, 'r')
	for line in if_handle :
		if line[0] == '#' :
			continue
		doc = add_line_to_map(line, doc)
	if_handle.close()
	for id in doc :
		doc[id].reduce()
	return doc

def info() :
	global dir
	print('\n\tWelcome to Nick\'s Paralogy Extractor 2000\n')
	print('Look inside directory \'%s\' to find paralog sets.\n' %dir)

def main() :
	info()
	parser = argparse.ArgumentParser()
	parser.add_argument('filename', help='The file you want to extract paralogs from (in disco or multiparanoid format)', metavar='solution.disco')
	args = parser.parse_args()
	filename = args.filename
	print('Reading %s'%filename)
	cluster_map = gather_paralogs(filename)
	print('Done reading.')
	write_clusters(cluster_map)
	print('Done.')

if __name__ == '__main__' :
	main()

