#! /bin/env python

import subprocess
import sys
import re
import argparse

debugging = False

def print_info() :
	print("")
	print("This script takes one argument (fasta alignment) and does the following:")
	print ("")
	print (" Output 1 (saved in FILENAME_best_in_species.fasta)")
	print ("\tIf any duplicates exist for a species, it picks the one with the most nucleotide [ATGCatgc] data")
	print ("\tThis output file has exactly one sequence per species")
	print ("")
	print (" Output 2 (saved in FILENAME_best_in_genus.fasta")
	print ("\tOut of all species in a genus, it picks the one with the most nucleotide data")
	print ("\tThis output file has exactly one sequence per genus (from the species with the most data)")
	print ("")
	print (' Output format:')
	print ('\tOutput is in aligned fasta format. Once organisms have been removed,')
	print ('\tall resulting empty columns (places where every sequence has -, ?, n, or N)')
	print ('\tare removed, so the alignments are clean and trimmed.')
	print ('')

def printdebug(msg) :
	if debugging :
		print(msg)

# Most often, this object actually holds a Header (name) and string (seq).
class Pair(object) :
	def __init__(self, name, seq) :
		self.name = name
		self.seq = seq

# I created this class because I had to keep track of which header specifically was kept.
# The duplicate species have a number after their name. The script needs to keep track of
# that number, while treating the species as duplicates (ignoring the number for comparisons)
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
			printdebug("(This is probably not an error) Did not find a species for genus in line : %s" %self.header)
			species = ''
		else :
			species = line[1]
		genus = line[0]
		if genus == 'Out' or genus == 'out' :
			if len(line) < 3 :
				printdebug("(This is probably not an error) Did not find a species for genus in line : %s" %self.header)
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


def parse_input(filename, data) :
	in_file = open(filename, 'r')
	print ("Parsing input.")
	header = Header('')
	for line in in_file :
		line = line.strip()
		if line == '' :
			continue
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

nucs = ['A', 'T', 'C', 'G', 'a', 't', 'c', 'g']
def calc_nuc_percent(seq, length) :
	global nucs
	count = 0
	for char in seq :
		if char in nucs :
			count += 1
	return (1.0 * count) / length

# This puts the best sequence at index 0 of the list (argument data map goes from header to list of Pair sequences)
# It returns a map from Header to Pair
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
		best_pair = seq_pairs[best_index]
		# The map no longer goes to a list, but just to a pair object
		data[header] = best_pair
	return data

def write_data(ofile, seq_pair) :
	# Must access the header of the Header object. Sorry about the bad code, bro.
	ofile.write('%s\n' %seq_pair.name.header)
	seq_out = ''
	i = 0
	for char in seq_pair.seq :
		if i % 60 == 0 :
			seq_out = seq_out + '\n'
		seq_out = seq_out + char
		i += 1
	# This takes care of whitespace at beginning and end of string
	seq_out = seq_out.strip()
	ofile.write('%s\n' %seq_out)

def write_output(filename, data) :
	ofile = open(filename, 'w')
	for header in data :
		write_data(ofile, data[header])
	ofile.close()

# Produces a map from (genus) to list of (Header, sequence) pair objects
def map_from_genus(data) :
	from_genus = {}
	for header in data :
		seq_pair = data[header]
		genus = seq_pair.name.getGenus()
		if genus == '' :
			printdebug('Blank genus found for %s' %header.header)
		if genus not in from_genus :
			from_genus[genus] = []
		from_genus[genus].append(seq_pair)
	return from_genus

the_dump = ['N','n','-','?']
def is_garbage(pairs, pos) :
	global the_dump
	result = True
	for pair in pairs :
		if pair.seq[pos] not in the_dump :
			result = False
			break
	return result

def str_minus_index(str, pos) :
	return (str[:pos] + str[(pos+1):])

def remove_column(pairs, pos) :
	for pair in pairs :
		pair.seq = str_minus_index(pair.seq, pos).strip()
	return pairs

def reconstruct_map(pairs) :
	data = {}
	for pair in pairs :
		data[pair.name] = pair
	return data

# Assume that at this point, data has no duplicates
def remove_garbage_columns(data) :
	pairs = list(data.values())
	size = len(pairs[0].seq)
	i = 0
	while i < size :
		if is_garbage(pairs, i) :
			printdebug('Garbage at %d' %i)
			pairs = remove_column(pairs, i)
			size -= 1
		i += 1
	return reconstruct_map(pairs)

def export_headers_with_numbers(filename) :
	# NOTE: Be careful with this: because shell=True, shell commands will execute.
	# I tried to protect you with quotes around the filename variable.
	subprocess.call('egrep \'[0-9]+\' \'%s\' > \'%s_numbered_headers.txt\'' %(filename, filename), shell=True)

def run_part_1(args, data) :
	print ("Selecting best duplicates.")
	length = len((list(data.values())[0][0]).seq)
	printdebug('Alignment length is: %d' %length)
	data = remove_duplicates(data, length)
	data = remove_garbage_columns(data)
	print ("Writing output 1")
	ofname1 = "%s_best_in_species.fasta" %args[1].split('.')[0]
	write_output(ofname1, data)
	export_headers_with_numbers(ofname1)
	return data

def run_part_2(args, data) :
	print ("Collapsing to one species per genus.")
	genus_map = map_from_genus(data)
	length = len((list(genus_map.values())[0][0]).seq)
	printdebug('Alignment length is: %d' %length)
	data = remove_duplicates(genus_map, length)
	data = remove_garbage_columns(data)
	print ("Writing output 2")
	ofname2 = "%s_best_in_genus.fasta" %args[1].split('.')[0]
	write_output(ofname2, data)
	export_headers_with_numbers(ofname2)
	return data

def handle_args(args) :
	global debugging
	parser = argparse.ArgumentParser()
	parser.add_argument('input', help='Provide a location to alignment file.')
	parser.add_argument('--debug', help='This makes extra stuff print out for the debugger\'s benefit.', action='store_true')
	args = parser.parse_args()
	input = args.input
	debugging = args.debug
	printdebug('If you see this message, you are a developer. Congrats. Your terminal will soon be full of meaningful junk.')
	return input

def main(args) :
	print_info()
	input_file = handle_args(args)
	# data is a map from header to header-seq pair objects
	data = parse_input(input_file, {})
	data = run_part_1(args, data)
	run_part_2(args, data)
	print('Done.')

if __name__ == "__main__" :
	main(sys.argv)

