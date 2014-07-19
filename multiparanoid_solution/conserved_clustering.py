#! /bin/env python

import sys
import os
import subprocess
import timeit

# Species have only unique genes, no paralogy
# Conserved clusters have no missing organisms

# This script
# Takes disco solution to multiparanoid
# And associated fasta files and
# Creates cluster files

# Assume the following about filenames:
# If the peptide files have format "filename.pep"
# Then the DNA files have format "filename.fasta"

# Assume DNA fasta files are located in the current directory


#######################################################
# Algorithm:
#	For each fasta file
#		For each gene in fasta file
#			For cluster in clusters
#				if gene in cluster : save to cluster
#######################################################

timing = False
start = timeit.default_timer()

def checkpoint_time() :
	global timing
	global start
	if timing :
		checkpoint = timeit.default_timer()
		print 'Time so far: %d' %(checkpoint - start)

id_counter = 1
class Cluster(object) :
# genes  ===   map from organism to list of genes
# data   ===   map from organism to sequence data
	def __init__(self) :
		global id_counter
		self.id = id_counter
		id_counter = id_counter + 1
		self.genes = {}
		self.data = {}

	# Do not allow paralogs
	def is_valid(self, num_organisms) :
		if len(self.genes) != num_organisms :
			return False
		for key in self.genes :
			if len(self.genes[key]) != 1:
				return False
		return True

	def get_bin(self) :
		return len(self.genes)

	def get_id(self) :
		return self.id

	def add_gene(self, organism, orf) :
		if organism in self.genes :
			self.genes[organism].append(orf)
		else :
			self.genes[organism] = [orf]

	def get_all_names_sorted(self) :
		return sorted(self.genes.iterkeys())

	def print_all(self) :
		for key in self.genes :
			print key
			print self.genes[key]
			print key + ".fasta"

	def contains(self, organism, gene) :
		if organism in self.genes :
			if gene in self.genes[organism] :
				return True
		return False

	def give(self, organism, data) :
		self.data[organism] = data

	def save(self, out_file, all_names) :
		for organism in all_names :
			out_file.write('> %s\n' %organism)
			if organism in self.data :
				out_file.write(self.data[organism])
				out_file.write('\n')

def usage(program_path) :
	print '\nUsage: %s <number_of_organisms> [-pep or -dna] <solution.disco>\n' %program_path

id_counter = 1
def get_id() :
	global id_counter
	id_counter = id_counter + 1
	return (id_counter - 1)

# Input format:
# cluster	organism	gene
# Assumes num_organisms is an int
def read_multiparanoid(num_organisms, multiparanoid) :
	in_file = open(multiparanoid, 'r')
	clusters = []
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
			if cluster.is_valid(num_organisms) :
				clusters.append(cluster)
			cluster = Cluster()
		# line goes in current cluster
		cluster.add_gene(line[1].split('.')[0], line[2])
	in_file.close()
	return clusters


def give_gene_to_cluster(clusters, organism, gene, data) :
	if gene == '' or data == '' :
		return clusters
	for cluster in clusters :
		if cluster.contains(organism, gene) :
			cluster.give(organism, data)
			return clusters
	return clusters

def read_fastas(clusters, all_names, uses_dna) :
	for name in all_names :
		filename = name + '.pep'
		if uses_dna :
			filename = name + '.fasta'
		print 'Reading %s...' %filename
		in_file = open(filename, 'r')
		gene = ''
		data = ''
		for line in in_file :
			if line[0] == '>' :
				# Use previous gene
				clusters = give_gene_to_cluster(clusters, name, gene, data)
				# Prepare to get new gene
				line = line.strip()
				line = line.split(' ')
				if len(line) == 1 :
					gene = line[0][1:]
				else :
					gene = line[-1].split(':')[0]
				data = ''
			else :
				data = data + line
		in_file.close()
	return clusters

def write_cluster(cluster, all_names, multiparanoid, subscript) :
	# This is the slowest part of the program now.
#	print 'Writing cluster %d' %cluster.get_id()
	filename = "tmp_cluster"
	out_file = open(filename, 'w')
	cluster.save(out_file, all_names)
	out_file.close()
#	checkpoint_time()
#	print 'Running mafft ...'
	# this is to silence mafft
	nowhere = open(os.devnull, 'w')
	subprocess.call("mafft %s > %sconserved_mod_%s/cluster%d.fasta" %(filename, subscript, multiparanoid, cluster.get_id()), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
	os.remove(filename)
	checkpoint_time()

def main(args) :
	if len(args) != 4 or ( args[2] != '-pep' and args[2] != '-dna' ) :
		usage(args[0])
		return
	subscript = "pep_"
	if (args[2] == '-dna') :
		subscript = 'dna_'
	# Read multiparanoid
	print "Reading disco input"
	clusters = read_multiparanoid(int(args[1]), args[3])
	print "There are %d semi-conserved clusters." %len(clusters)
	if len(clusters) == 0 :
		return
	# Assume there is a cluster containing all the organisms
	big_cluster = clusters[0]
	all_names = big_cluster.get_all_names_sorted()

	# time
	checkpoint_time()
	
	# Read fasta files
	print "Gathering clusters"
	clusters = read_fastas(clusters, all_names, (args[2] == '-dna'))
	
	# time
	checkpoint_time()

	total = len(clusters)

	if not os.path.exists("%sconserved_mod_%s" %(subscript, args[3])) :
		os.makedirs("%sconserved_mod_%s" %(subscript, args[3]))


	counter = 0
	percent = total / 10
	if percent == 0 :
		percent = 1
	# Write aligned clusters
	for cluster in clusters :
		if counter % percent == 0 :
			print "Progress: %.2f%%" %(counter * 100.0 / total)
		write_cluster(cluster, all_names, args[3], subscript)
		counter += 1
	# time
	checkpoint_time()

if __name__ == "__main__" :
	main(sys.argv)

