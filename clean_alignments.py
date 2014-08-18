#! /bin/env python

import subprocess
import sys
import re

def print_info() :
	print("")
	print("This script takes one argument (fasta alignment) and does the following:")
	print ("")
	print (" Output 1 (saved in FILENAME_no_duplicates.fasta)")
	print ("\tIf any duplicates exist for a species, it picks the one with the most nucleotide [ATGCatgc] data")
	print ("\tThis output file has exactly one sequence per species")
	print ("")
	print (" Output 2 (saved in FILENAME_best_in_genus.fasta")
	print ("\tOut of all species in a genus, it picks the one with the most nucleotide data")
	print ("\tThis output file has exactly one sequence per genus (from the species with the most data)")
	print ("")


class Pair(object) :
	def __init__(self, name, seq) :
		self.name = name
		self.seq = seq


class Header(object) :
	def __init__(self, str) :
		self.header = str

	def parseHeader(self) :
		line = self.header
		line = line[1:]
		if '_' in line :
			line = line.split('_')
		else :
			line = line.split(' ')
		if len(line) < 2 :
			print("(This is probably not an error) Did not find a species for genus in line : %s" %self.header)
			species = ''
		else :
			species = line[1]
		genus = line[0]
		if genus == 'Out' or genus == 'out' :
			if len(line) < 3 :
				print ("(This is probably not an error) Did not find a species for genus in line : %s" %self.header)
				species = ''
			else :
				species = line[2]
			genus = line[1]
		# Remove all nonalpha chars from the species
		species = re.sub(r'[^a-zA-Z]', '', species)
		# Remove all nonalpha chars from the genus
		genus = re.sub(r'[^a-zA-Z]', '', genus)
		return "%s %s" %(genus, species)

	def __hash__(self) :
		return hash(self.parseHeader())
	def __eq__(self, other) :
		return (self.parseHeader() == other.parseHeader())
	def __ne__(self, other) :
		return (self.parseHeader() != other.parseHeader())

	def getGenus(self) :
		return self.parseHeader().split(' ')[0]

	def getSpecies(self) :
		name = self.parseHeader().split(' ')
		sp == ''
		if len(name) > 1 :
			sp = name[1]
		return sp


nucs = ['A', 'T', 'C', 'G', 'a', 't', 'c', 'g']
def calc_nuc_percent(seq, length) :
	global nucs
	count = 0
	for char in seq :
		if char in nucs :
			count += 1
	return (1.0 * count) / length

def parse_input(filename, data) :
	in_file = open(filename, 'r')
	print ("Parsing input.")
	header = Header('')
	for line in in_file :
		line = line.strip()
		if line[0] == '>' :
			if header.header != '' :
				if header not in data :
					data[header] = []
				data[header].append(Pair(header, seq))
			header = Header(line)
			seq = ''
		else :
			seq += line
	# Take care of the last sequence in the file
	if header not in data :
		data[header] = []
	data[header].append(Pair(header, seq))
	in_file.close()
	return data

# This puts the best sequence at index 0 of the list (data map goes from header to list of sequences)
def remove_duplicates(data, length) :
	for header in data :
		seq_pairs = data[header]
		size = len(seq_pairs)
		best_percent = 0.0
		best_index = -1
		for i in range(0, size) :
			percent = calc_nuc_percent(seq_pairs[i].seq, length)
			if percent > best_percent :
				best_percent = percent
				best_index = i
		# note that 
		best_pair = seq_pairs[best_index]
		data[header] = [best_pair]
	return data

def contains_duplicates(data) :
	for header in data :
		array = data[header]
		if len(array) != 1 :
			return True
	return False

def write_data_at_position(out_file, data, header, index) :
	seq_pair = data[header][index]
	# Must access the header of the Header object. Sorry about the bad code, bro.
	out_file.write('%s\n' %seq_pair.name.header)
	seq_out = ''
	i = 0
	for char in seq_pair.seq :
		if i % 60 == 0 :
			seq_out = seq_out + '\n'
		seq_out = seq_out + char
		i += 1
	if seq_out[0] == '\n' :
		seq_out = seq_out[1:]
	seq_out.strip()
	out_file.write('%s\n' %seq_out)

def write_output(filename, data) :
	of = open(filename, 'w')
	for header in data :
		# Index 0 is the best sequence for this species
		write_data_at_position(of, data, header, 0)
	of.close()

# Produces a map from (genus) to list of (name, sequence) pair objects
def map_from_genus(data) :
	from_genus = {}
	for header in data :
		seq_pair = data[header][0]
		genus = seq_pair.name.getGenus()
		if genus == '' :
			print('Blank genus found for %s' %header.header)
		if genus not in from_genus :
			from_genus[genus] = []
		from_genus[genus].append(seq_pair)
	return from_genus

def collapse_genus(genus_map, length) :
	data = {}
	for genus in genus_map :
		best_seq_pair = ''
		best_per = 0.0
		for pair in genus_map[genus] :
			percent = calc_nuc_percent(pair.seq, length)
			if percent > best_per :
				best_per = percent
				best_seq_pair = pair
		if best_seq_pair.seq == '' or best_seq_pair.name.header == '' and genus != '' :
			print ("Possible error, something is blank for name, seq: %s, %s" %(best_seq_pair.name, best_seq_pair.seq))
			print ("Genus %s has no output." %genus)
		data[best_seq_pair.name] = [best_seq_pair]
	return data

def export_headers_with_numbers(filename) :
	# NOTE: Be careful with this: because shell=True, shell commands will execute.
	# I tried to protect you with quotes around the filename variable.
	subprocess.call('egrep \'[0-9]+\' \'%s\' > \'%s_numbered_headers.txt\'' %(filename, filename), shell=True)

def run_part_1(args, data, length) :
	print ("Selecting best duplicates.")
	data = remove_duplicates(data, length)
	if contains_duplicates(data) :
		print ("ERROR: Duplicates remain!")
	print ("Writing output 1")
	ofname1 = "%s_no_duplicates.fasta" %args[1].split('.')[0]
	write_output(ofname1, data)
	export_headers_with_numbers(ofname1)
	return data

def run_part_2(args, data, length) :
	print ("Collapsing to one species per genus.")
	genus_map = map_from_genus(data)
	data = collapse_genus(genus_map, length)
	print ("Writing output 2")
	ofname2 = "%s_best_in_genus.fasta" %args[1].split('.')[0]
	write_output(ofname2, data)
	export_headers_with_numbers(ofname2)
	return data

def main(args) :
	print_info()
	if len(args) != 2 :
		print ("INCORRECT ARGUMENTS")
		print ("Usage: %s <alignment_file.fasta>")
		return 1
	# data is a map from header to header-seq pair objects
	data = parse_input(args[1], {})
	length = len((list(data.values())[0][0]).seq)
	data = run_part_1(args, data, length)
	run_part_2(args, data, length)

if __name__ == "__main__" :
	main(sys.argv)

