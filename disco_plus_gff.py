#! /bin/env python

import sys
import os
import subprocess
import timeit

def info() :
	print('Species have only unique genes, no paralogy')
	print('')
	print('This script:')
	print('Takes disco solution to multiparanoid')
	print('And associated gff files')
	print('Producing a file with clusters (semi or conserved) with GO terms')
	print('' )
	print('Assumes the following about file names:')
	print('For each organism present in the disco file,')
	print('there is a gff file named organism.gff')
	print('' )
	print('OUTPUT FORMAT:')
	print('Cluster	Species	Gene	GO-terms')

class Annotation(object) :
	def __init__(self) :
		self.gene = ''
		self.terms = set()

	def set_gene(self, g) :
		self.gene = g

	def add_term(self, term) :
		self.terms.add(term)


class Cluster(object) :
# genes  ===   map from organism to list of Annotation)
	def __init__(self) :
		self.genes = {}

	# Do not allow paralogs
	def is_valid(self, num_organisms) :
		global conserved
		if conserved and len(self.genes) != num_organisms :
			return False
		for key in self.genes :
			if len(self.genes[key]) != 1:
				return False
		return True

	def get_bin(self) :
		return len(self.genes)

	def add_gene(self, organism, orf_id) :
		data = Annotation()
		data.set_gene(orf_id)
		if organism in self.genes :
			self.genes[organism].append(data)
		else :
			self.genes[organism] = [data]

	def get_all_names_sorted(self) :
		return sorted(list(self.genes.keys()))

	def contains(self, organism, gene) :
		if organism in self.genes :
			for data in self.genes[organism] :
				if gene == data.gene :
					return True
		return False

	def add_go_term(self, organism, gene, go_term) :
		if not self.contains(organism, gene) :
			return False
		# Length must be 1 (no paralogs), so index 0 is only index allowed.
		self.genes[organism][0].add_term(go_term)
		return True

	def write(self, out_file, counter) :
		for organism in self.genes :
			annotation = self.genes[organism][0]
			out_file.write('%d\t%s\t%s\t' %(counter, organism, annotation.gene))
			if len(annotation.terms) == 0 :
				out_file.write('-')
			else :
				for term in annotation.terms :
					out_file.write('%s ' %term)
			out_file.write('\n')


# Input format:
# cluster	organism	gene
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
		print('There are %d clusters in bin %d' %(len(clusters[bin]), bin))
	return clusters


def give_go_term(clusters, organism, gene, term) :
	if gene == '' or term == '' or term == '':
		return clusters
	for key in clusters :
		for cluster in clusters[key] :
			if cluster.add_go_term(organism, gene, term) :
				return clusters
	return clusters

def parse_terms(clusters, name, gene, attr) :
	terms = attr.split('GO:')
	for part in terms :
		valid = True
		for i in range(0,7) :
			if not part[i].isdigit() :
				valid = False
		if valid :
			term = 'GO:%s' %part[0:7]
			clusters = give_go_term(clusters, name, gene, term)

def parse_gff_line(line, clusters, name):
	if line[0] == '#' :
		return
	attr = line.strip().split('\t')[8]
	gene = attr.split(' ')[0]
	parse_terms(clusters, name, gene, attr)

def read_all_gff_files(clusters, all_names) :
	for name in all_names :
		filename = name + '.gff'
		print('Reading %s...' %filename)
		in_file = open(filename, 'r')
		gene = ''
		term = ''
		for line in in_file :
			parse_gff_line(line, clusters, name)
		in_file.close()
	return clusters

def usage(program_path) :
	print('\nUsage: %s <number_of_organisms> [-c (conserved) or -s (semiconserved)] <solution.disco>\n' %program_path)

conserved = True

def handleArgs(args) :
	global conserved
	if len(args) != 4 or ( args[2] != '-c' and args[2] != '-s' ) :
		usage(args[0])
		return
	if (args[2] == '-s') :
		conserved = False
		print('Finding semiconserved clusters.')
	else :
		print('Finding conserved clusters.')
	return True

def get_all_names(clusters, num_species) :
	# Assume there is a cluster containing all the organisms
	# Look in bin given by num_species
	big_cluster = clusters[num_species][0]
	all_names = big_cluster.get_all_names_sorted()

	if len(all_names) != num_species :
		print('Oh, no! We didn\'t get a cluster with all the organisms represented!')
	return all_names

# OUTPUT FORMAT
# Cluster	Species	Gene	GO-terms
def write_output(clusters, total, out_file) :
	print('Writing output.')
	out_file.write('#Cluster\tSpecies\tGene    \tGO-terms\n')
	counter = 1
	# Write aligned clusters
	for bin in clusters :
		for cluster in clusters[bin] :
			cluster.write(out_file, counter)
			counter += 1

def main(args) :
	global conserved
	if not handleArgs(args) :
		return
	# Read multiparanoid
	print('Reading disco input')
	clusters = read_multiparanoid(int(args[1]), args[3])
	if len(clusters) == 0 :
		return

	all_names = get_all_names(clusters, int(args[1]))
	
	# Read gff file
	print("Gathering clusters")
	clusters = read_all_gff_files(clusters, all_names)

	total = 0
	for bin in clusters :
		total += len(clusters[bin])
	print('There are %d clusters in total.' %total)

	filename = '%s_semiconserved_terms' %args[3]
	if conserved :
		filename = '%s_conserved_terms' %args[3]

	out_file = open(filename, 'w')
	write_output(clusters, total, out_file)
	out_file.close()

if __name__ == "__main__" :
	main(sys.argv)

