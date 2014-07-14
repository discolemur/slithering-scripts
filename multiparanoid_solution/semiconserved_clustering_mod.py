#! /bin/env python

import sys
import os
import subprocess
import timeit

# Species have only unique genes, no paralogy
# Missing species are filled in with dashes after alignment
# Clusters have a bin number for how many organisms are present in each cluster


# This script
# Takes multiparanoid output
# And associated fasta files and
# Creates a supermatrix

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

	def is_valid(self, num_organisms) :
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
	print '\nUsage: %s <number_of_organisms> <multiparanoid_output.sql>\n' %program_path

id_counter = 1
def get_id() :
	global id_counter
	id_counter = id_counter + 1
	return (id_counter - 1)

# Assumes num_organisms is an int
def read_multiparanoid(num_organisms, multiparanoid) :
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
			if cluster.is_valid(num_organisms) :
				bin = cluster.get_bin()
				if bin in clusters :
					clusters[bin].append(cluster)
				else :
					clusters[bin] = [cluster]
			cluster = Cluster()
		# line goes in current cluster
		cluster.add_gene(line[1].split('.')[0], line[2])
	in_file.close()
	if 0 in clusters :
		del clusters[0]
	for bin in clusters :
		print 'There are %d clusters in bin %d' %(len(clusters[bin]), bin)
	return clusters

def give_gene_to_cluster(clusters, organism, gene, data) :
	if gene == '' or data == '' :
		return clusters
	for key in clusters :
		for cluster in clusters[key] :
			if cluster.contains(organism, gene) :
				cluster.give(organism, data)
				return clusters
	return clusters

def read_fastas(clusters, all_names) :
	for name in all_names :
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
				gene = line[1:]
				data = ''
			else :
				data = data + line
		in_file.close()
	return clusters

def write_cluster(cluster, all_names) :
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
	subprocess.call("mafft %s > cluster%d_bin%d.fasta" %(filename, cluster.get_id(), cluster.get_bin()), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
	os.remove(filename)
	checkpoint_time()

def main(args) :
	if len(args) != 3 :
		usage(args[0])
		exit()

	# Read multiparanoid
	clusters = read_multiparanoid(int(args[1]), args[2])
	# Assume there is a cluster containing all the organisms
	big_cluster = clusters[int(args[1])][0]
	all_names = big_cluster.get_all_names_sorted()

	# time
	checkpoint_time()
	
	# Read fasta files
	clusters = read_fastas(clusters, all_names)

	# time
	checkpoint_time()

	total = 0.0
	for bin in clusters :
		total += len(clusters[bin])

	counter = 0.0
	# Write aligned clusters
	for key in clusters :
		for cluster in clusters[key] :
			write_cluster(cluster, all_names)
			counter += 1
		print "Progress: %f.2\%" %(counter * 100 / total)
	# time
	checkpoint_time()

if __name__ == "__main__" :
	main(sys.argv)

