#! /bin/env python

import sys
import glob

# workfile:
# global_cluster_id	unique_sp/gene

# map:
# unique_sp/gene actual_sp/gene


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


cluster_counter = 1
id_counter = 1

prev_output_line = ""

# Reads file, updates map, and writes clusters to work file
def read_file(all_genes, infile, workfile) :
	global id_counter
	global cluster_counter
	global prev_output_line
	prev_cluster = '-1'
	cluster_data = set()
	for line in infile :
		line = line.strip()
		line = line.split('\t')
		if line[0] != prev_cluster :
			# new cluster
			for output_line in cluster_data :
				workfile.write(output_line)
			cluster_counter += 1
			prev_cluster = line[0]
			cluster_data = set()
		next = species_gene(line[2], line[4])
		id = -1
		if next in all_genes :
			id = all_genes[next]
		else :
			all_genes[next] = id_counter
			id = id_counter
			id_counter += 1
		output_line = "%d\t%d\n" %(cluster_counter, id)
		cluster_data.add(output_line)
	cluster_counter += 1
	return all_genes

def main(args) :
	all_genes = {}
	files = glob.glob("sqltable.*")
	counter = 1
	total = len(files)
	print("Reading files and writing work file (combined.disco).")
	workfile = open("combined.disco", 'w')
	workfile.write("#global_cluster_id\tgene_organism_id\n")
	for file in files :
		print("Reading file: %s (%d/%d) %.2f . . . " %(file, counter, total, ((counter*100.0)/total)))
		infile = open(file, 'r')
		all_genes = read_file(all_genes, infile, workfile)
		infile.close()
		counter += 1
	workfile.close()
	mapfile = open("map.disco", 'w')
	mapfile.write("#gene_organism_id\torganism\tgene\n")
	print("Writing map to map.disco . . . ")
	for elem in all_genes :
		mapfile.write("%d\t%s\t%s\n" %(all_genes[elem], elem.species, elem.gene))
	mapfile.close()
	print('Done writing map.disco')

if __name__ == "__main__" :
	main(sys.argv)
