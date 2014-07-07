#! /bin/env python

import sys

# Input format:
# aggregate_cluster_id	global_cluster_id	gene_organism_id

# Map format:
# gene_organism_id	organism	gene

# Output format:
# aggregate_cluster_id	organism	gene

class species_gene :
	def __init__(self, sp, ge) :
		self.species = sp
		self.gene = ge

	def __hash__(self) :
		return hash("%s%s" %(self.species, self.gene))

	def __eq__(self, other) :
		return (self.species == other.species and self.gene == other.gene)

	def __ne__(self, other) :
		return (self.species != other.species or self.gene != other.gene)

def create_output(data, map, output) :
	output.write("# cluster\torganism\tgene\n")
	used = []
	for row in data :
		individual = map[row[2]]
		line = "%s\t%s\t%s\n" %(row[0], individual.species, individual.gene)
		if line not in used :
			used.append(line)
			output.write(line)

def sort_input(input) :
	data = []
	for line in input :
		if line[0] == '#' :
			continue
		line = line.strip()
		line = line.split('\t')
		data.append(line)
	return sorted(data)

def read_map(mapfile) :
	keys = []
	values = []
	# map from gene_organism_id to <gene organism> object
	for line in mapfile :
		if line[0] == '#' :
			continue
		line = line.strip()
		line = line.split('\t')
		keys.append(line[0])
		sp = species_gene(line[1], line[2])
		values.append(species_gene(line[1], line[2]))
	data = dict(zip(keys, values))
	if len(data) != len(keys) :
		print "ERROR IN KEY FILE! MULTIPLE DEFINITIONS FOR A KEY!\n"
		return None
	return data

def main(args) :
	if (len(args) != 4) :
		print "Usage: %s <input_filename> <map.disco> <output_filename>" %args[0]
		exit(1)
	mapfile = open(args[2], 'r')
	map = read_map(mapfile)
	output = open(args[3], 'w')
	input = open(args[1], 'r')
	data = sort_input(input)
	create_output(data, map, output)
	mapfile.close()
	input.close()
	output.close()

if __name__ == "__main__" :
	main(sys.argv)
