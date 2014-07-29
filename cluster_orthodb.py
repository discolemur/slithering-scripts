#! /bin/env python

import sys
import os
import subprocess
import timeit

# Species have only unique genes, no paralogy
# Missing species are filled in with dashes after alignment
# Clusters have a bin number for how many organisms are present in each cluster


# This script
# Takes orthodb text file
# And associated orthodb fasta file and
# Produces clusters (conserved)

# Assume the following about filenames:
# If the peptide files have format "filename.pep"
# Then the DNA files have format "filename.fasta"

# Assume DNA/AA fasta files are located in the current directory

#######################################################
# Algorithm:
#	For each fasta file
#		For each gene in fasta file
#			For cluster in clusters
#				if gene in cluster : save to cluster
#######################################################

timing = True
start = timeit.default_timer()

def checkpoint_time() :
	global timing
	global start
	if timing :
		checkpoint = timeit.default_timer()
		print 'Time so far: %d' %(checkpoint - start)

class Cluster(object) :
# genes  ===   map from organism to list of genes
# data   ===   map from organism to sequence data
	def __init__(self) :
		self.genes = {}
		self.data = {}

	# Do not allow paralogs
	def is_valid(self, num_organisms) :
		if len(self.genes) != num_organisms :
	#		print 'Invalid cluster: has %d organisms' %len(self.genes)
			return False
		for key in self.genes :
			if len(self.genes[key]) != 1:
	#			print 'Invalid: has paralogy with %s, %s' %(key, self.genes[key])
				return False
		return True

	def get_bin(self) :
		return len(self.genes)

	def add_gene(self, organism, gene) :
		if organism in self.genes :
			self.genes[organism].append(gene)
		else :
			self.genes[organism] = [gene]

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
		if organism not in self.data :
			self.data[organism] = data

	def save(self, out_file, all_names, counter) :
		for organism in all_names :
			out_file.write('>%d|%s|%s\n' %(counter, organism, self.genes[organism][0]))
			if organism in self.data :
				out_file.write(self.data[organism])
				out_file.write('\n')
# Input format:
# Cluster	gene	protein	organism	name	code	length	...
# Assumes num_organisms is an int
def read_txt(num_organisms, txt) :
	in_file = open(txt, 'r')
	clusters = {}
	prev = ''
	cluster = Cluster()
	for line in in_file :
		line = line.strip()
		line = line.split('\t')
		# line indicates a new cluster
		if prev != line[0] :
			prev = line[0]
			if cluster.is_valid(num_organisms) :
				bin = cluster.get_bin()
				if bin in clusters :
					clusters[bin].append(cluster)
				else :
					clusters[bin] = [cluster]
			cluster = Cluster()
		# line goes in current cluster
		organism = line[5]
		gene = line[1]
#		print 'Organism: %s, Gene: %s' %(organism, gene)
		cluster.add_gene(organism, gene)
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

def read_fasta(clusters, all_names, fasta) :
	total = sum(1 for line in open(fasta))
	print 'Reading %s...' %fasta
	in_file = open(fasta, 'r')
	count = 0
	percent = total / 10
	gene = ''
	data = ''
	organism = ''
	for line in in_file :
		if line[0] == '>' :
			# Use previous gene
			clusters = give_gene_to_cluster(clusters, organism, gene, data)
			# Prepare to get new gene
			line = line.strip()
			line = line[1:]
			line = line.split(' ')
			gene = line[0]
			organism = line[-1]
			data = ''
		else :
			data = data + line
		count += 1
		if count % percent == 0 :
			print "Progress: %.2f%%" %(count * 100.0 / total)
	give_gene_to_cluster(clusters, organism, gene, data)
	in_file.close()
	return clusters

def write_cluster(cluster, all_names, txt, counter) :
	# This is the slowest part of the program now.
#	print 'Writing cluster %d' %counter
	filename = "tmp_cluster"
	out_file = open(filename, 'w')
	cluster.save(out_file, all_names, counter)
	out_file.close()
#	print 'Running mafft ...'
	# this is to silence mafft
	nowhere = open(os.devnull, 'w')
	subprocess.call("mafft %s > conserved_%s/cluster%d.aln" %(filename, txt, counter), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
	os.remove(filename)

def mkdirs(name) :
	if not os.path.exists("conserved_%s" %(name)) :
		os.makedirs("conserved_%s" %(name))


def usage(program_path) :
	print '\nUsage: %s <number_of_organisms> <orthodb.txt> <orthodb.fasta>\n' %program_path


def main(args) :
	if len(args) != 4 :
		usage(args[0])
		return
	print 'Running conserved clustering.'
	print 'Reading txt input'
	clusters = read_txt(int(args[1]), args[2])
	if len(clusters) == 0 :
		print 'No clusters found.'
		return
	# Assume there is a cluster containing all the organisms
	# Look in bin given by args[1] (number of organisms)
	big_cluster = clusters[int(args[1])][0]
	all_names = big_cluster.get_all_names_sorted()

	# time
	checkpoint_time()
	
	# Read fasta file
	print "Gathering clusters"
	clusters = read_fasta(clusters, all_names, args[3])
	
	# time
	checkpoint_time()

	total = 0
	for bin in clusters :
		total += len(clusters[bin])
	
	print 'There are %d clusters in total.' %total 

	mkdirs(args[2])

	counter = 1
	percent = total / 10
	if percent == 0 :
		percent = 1
	# Write aligned clusters
	for bin in clusters :
		for cluster in clusters[bin] :
			if counter % percent == 0 :
				print "Progress: %.2f%%" %(counter * 100.0 / total)
				checkpoint_time()
			write_cluster(cluster, all_names, args[2], counter)
			counter += 1
	print "Done."
	# time
	checkpoint_time()

if __name__ == "__main__" :
	main(sys.argv)

