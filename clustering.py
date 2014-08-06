#! /bin/env python

import sys
import os
import subprocess
import timeit

def info() :
	print 'Species have only unique genes, no paralogy'
	print 'Missing species are filled in with dashes after alignment'
	print 'Clusters have a bin number for how many organisms are present in each cluster'
	print ''
	print 'This script'
	print 'Takes disco solution to multiparanoid'
	print 'And associated fasta files and'
	print 'Produces clusters (conserved or semiconserved)'
	print ''
	print 'Assume the following about filenames:'
	print 'If the peptide files have format filename.pep'
	print 'Then the DNA files have format filename.fasta'
	print ''
	print 'Assume DNA/AA fasta files are located in the current directory'

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

class Cluster(object) :
# genes  ===   map from organism to list of genes
# data   ===   map from organism to sequence data
	def __init__(self) :
		self.genes = {}
		self.data = {}

	# Do not allow paralogs
	def is_valid(self, num_organisms) :
		global conserved
		if conserved and len(self.genes) != num_organisms :
			return False
		for key in self.genes :
			if len(self.genes[key]) != 1:
				return False
		print self.genes
		return True

	def get_bin(self) :
		return len(self.genes)

	def add_gene(self, organism, id) :
		if organism in self.genes :
			self.genes[organism].append(id)
		else :
			self.genes[organism] = [id]

	def get_all_names_sorted(self) :
		return sorted(self.genes.iterkeys())

	def print_all(self) :
		for key in self.genes :
			print 'organism: %s' %key
			print 'genes:'
			print self.genes[key]

	def contains(self, organism, gene) :
		if organism in self.genes :
			if gene in self.genes[organism] :
				print '1'
				return True
		return False

	def set_sequence(self, organism, seq) :
		self.data[organism] = seq
		print '2'

	def save(self, out_file, all_names, counter) :
		if len(self.data) == 0 :
			print 'ERROR! All sequences were lost in this cluster %d.' %counter
			out_file.write('ERROR! All sequences were lost in this cluster %d.' %counter)
			return
		for organism in all_names :
			id = ''
			if organism in self.genes :
				id = self.genes[organism][0]
			out_file.write('>%d|%s|%s\n' %(counter, organism, id))
			if organism in self.data :
				seq = self.data[organism]
				out_file.write(seq)
				out_file.write('\n')

def add_cluster(clusters, cluster, num_organisms) :
	if cluster.is_valid(num_organisms) :
		bin = cluster.get_bin()
		if bin in clusters :
			clusters[bin].append(cluster)
		else :
			clusters[bin] = [cluster]
	return clusters

# Input format:
# cluster	organism.pep	gene
# Assumes num_organisms is an int
def read_multiparanoid(num_organisms, multiparanoid) :
	print 'Reading %s . . .' %multiparanoid
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
		print 'There are %d clusters in bin %d' %(len(clusters[bin]), bin)
	return clusters

def give_gene_to_cluster(clusters, organism, id, seq) :
	if id == '' or seq == '' :
		return clusters
	for key in clusters :
		for cluster in clusters[key] :
			if cluster.contains(organism, id) :
				cluster.set_sequence(organism, seq)
				return clusters
	return clusters

def get_gene_id(line, uses_dna) :
	id = ''
	line = line.strip()
	# Remove '>'
	line = line[1:]
	line = line.split(' ')
	if line[0] == '' :
		line = line[1:]
	# Handle simple case and normal fasta format case
	if uses_dna or len(line) == 1:
		id = line[0]
	# Handle complex case for transdecoder headers
	elif not uses_dna :
		id = line[-1].split(':')[0]
	else :
		print 'Error: unable to parse header.'
	return id

def read_fastas(clusters, all_names, uses_dna) :
	for name in all_names :
		filename = name + '.pep'
		if uses_dna :
			filename = name + '.fasta'
		print 'Reading %s...' %filename
		in_file = open(filename, 'r')
		id = ''
		seq = ''
		for line in in_file :
			if line[0] == '>' :
				# Use previous gene
				if seq == '' and id != '' :
					print 'Error: did not get gene sequence for id %s' %id
				clusters = give_gene_to_cluster(clusters, name, id, seq)
				# Prepare to get new gene
				id = get_gene_id(line, uses_dna)
				if id == '' :
					print 'Error: did not parse gene id from %s' %line
				seq = ''
			else :
				seq = seq + line
		in_file.close()
	return clusters

def write_cluster(cluster, all_names, multiparanoid, subscript, counter) :
#	print 'Writing cluster %d' %counter
	filename = "tmp_%s_%d_%s_%d" %(subscript, counter, multiparanoid, cluster.get_bin())
	out_file = open(filename, 'w')
	cluster.save(out_file, all_names, counter)
	out_file.close()
#	checkpoint_time()
#	print 'Running mafft ...'
	# this is to silence mafft
	nowhere = open(os.devnull, 'w')
	if conserved :
		subprocess.call("mafft %s > %sconserved_%s/cluster%d.aln" %(filename, subscript, multiparanoid, counter), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
	else :
		subprocess.call("mafft %s > %ssemiconserved_%s/cluster%d_bin%d.aln" %(filename, subscript, multiparanoid, counter, cluster.get_bin()), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
	os.remove(filename)
	checkpoint_time()

def mkdirs(name, subscript) :
	global conserved
	if conserved :
		if not os.path.exists("%sconserved_%s" %(subscript, name)) :
			os.makedirs("%sconserved_%s" %(subscript, name))
	else :
		if not os.path.exists("%ssemiconserved_%s" %(subscript, name)) :
			os.makedirs("%ssemiconserved_%s" %(subscript, name))


def usage(program_path) :
	print '\nUsage: %s <number_of_organisms> [-pep or -dna] [-c (conserved) or -s (semiconserved)] <solution.disco>\n' %program_path

conserved = True

def main(args) :
	global conserved
	info()
	if len(args) != 5 or ( args[2] != '-pep' and args[2] != '-dna' ) or ( args[3] != '-c' and args[3] != '-s' ) :
		usage(args[0])
		return
	subscript = "pep_"
	if (args[2] == '-dna') :
		subscript = 'dna_'
	if (args[3] == '-s') :
		conserved = False
		print 'Running semiconserved clustering.'
	else :
		print 'Running conserved clustering.'
	# Read multiparanoid
	print 'Reading disco input'
	clusters = read_multiparanoid(int(args[1]), args[4])
	if len(clusters) == 0 :
		return
	# Assume there is a cluster containing all the organisms
	# Look in bin given by args[1] (number of organisms)
	big_cluster = clusters[int(args[1])][0]
	all_names = big_cluster.get_all_names_sorted()

	# time
	checkpoint_time()
	
	# Read fasta files
	print "Gathering clusters"
	clusters = read_fastas(clusters, all_names, (args[2] == '-dna'))
	
	# time
	checkpoint_time()

	total = 0
	for bin in clusters :
		total += len(clusters[bin])
	
	print 'There are %d clusters in total.' %total 

	mkdirs(args[4], subscript)

	counter = 1
	percent = total / 10
	if percent == 0 :
		percent = 1
	# Write aligned clusters
	for bin in clusters :
		for cluster in clusters[bin] :
			if counter % percent == 0 :
				print "Progress: %.2f%%" %(counter * 100.0 / total)
			write_cluster(cluster, all_names, args[4], subscript, counter)
			counter += 1
	# time
	checkpoint_time()

if __name__ == "__main__" :
	main(sys.argv)

