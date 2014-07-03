#! /bin/env python

import sys

import os

import subprocess

# This script
# Takes multiparanoid output
# And associated fasta files and
# Creates a supermatrix of conservative clusters

# Assume the following about filenames:
# If the peptide files have format "filename.pep"
# Then the DNA files have format "filename.fasta"

# Assume DNA fasta files are located in the current directory

class Cluster(object) :
# map from organism to list of genes
	def __init__(self) :
		self.genes = {}

	def is_valid(self, num_organisms) :
		if len(self.genes) != num_organisms :
#			print 'bad nums'
#			print self.genes
			return False
		for key in self.genes :
			if len(self.genes[key]) != 1:
#				print 'bad organism'
#				print key
#				print self.genes[key]
				return False
#		print "valid"
#		print self.genes
		return True

	def add_gene(self, organism, orf) :
		if organism in self.genes :
			self.genes[organism].append(orf)
		else :
			self.genes[organism] = [orf]

	# It is important to sort the keys so that the organisms are always in the same order
	def write_output(self, out_file, uses_dna) :
		for key in sorted(self.genes.iterkeys()) :
			filename = key
			if (uses_dna) :
				filename = filename + '.fasta'
			else :
				filename = filename + '.pep'
			in_file = open(filename, 'r')
			getting = False
			for line in in_file :
				line = line.strip()
				if line[0] == '>' :
					if getting :
						break
					if line[1:] == self.genes[key][0] :
#						print line[1:]
#						print self.genes[key][0]
						getting = True
				if getting :
					out_file.write(line)
					if line[0] == '>' :
						out_file.write(" %s" %key);
					out_file.write('\n')
			in_file.close()

	def print_all(self) :
		for key in self.genes :
			print key
			print self.genes[key]
			print key + ".fasta"


def usage(program_path) :
	print '\nUsage: %s <number_of_organisms> [-pep or -dna] <multiparanoid_output.sql>\n' %program_path

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

def mine_clusters(clusters, uses_dna) :
	i = 1
	for cluster in clusters :
		filename = "%d_tmp" %i
		out_file = open(filename, 'w')
		cluster.write_output(out_file, uses_dna)
		i += 1
		out_file.close()
		nowhere = open(os.devnull, 'w')
		subprocess.call("mafft %s > cluster%d.fasta" %(filename, i), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
		os.remove(filename)

def main(args) :
	if len(args) != 4 or ( args[2] != '-pep' and args[2] != '-dna' ) :
		usage(args[0])
		exit()
	clusters = read_multiparanoid(int(args[1]), args[3])
	mine_clusters(clusters, (args[2] == '-dna') )

if __name__ == "__main__" :
	main(sys.argv)

