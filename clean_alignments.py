#! /bin/env python

import subprocess
import sys
import re
import argparse

debugging = False
simple = False

def print_info() :
	print("")
	print("This script takes one argument (fasta alignment) and does the following:")
	print("")
	print(" Output 1 (saved in FILENAME_best_in_species.fasta)")
	print("\tIf any duplicates exist for a species, it picks the one with the most nucleotide [ATGCatgc] data")
	print("\tThis output file has exactly one sequence per species")
	print("")
	print(" Output 2 (saved in FILENAME_best_in_genus.fasta")
	print("\tOut of all species in a genus, it picks the one with the most nucleotide data")
	print("\tThis output file has exactly one sequence per genus (from the species with the most data)")
	print("")
	print(' Output format:')
	print('\tOutput is in fasta format.')
	print('\tIf input was aligned: once organisms have been removed,')
	print('\tall resulting empty columns (places where every sequence has -, ?, n, or N)')
	print('\tare removed, so the alignments are clean and trimmed.')
	print('')

def printdebug(msg) :
	if debugging :
		print(msg)

# Most often, this object actually holds a Header (name) and string (seq).
class Gene(object) :
	def __init__(self, name, seq) :
		self.name = name
		self.seq = seq
		printdebug(seq)

	def remove_number(self) :
		self.name.remove_number()

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

	def remove_number(self) :
		while re.match('.*[0-9]+$', self.header) :
			self.header = self.header[:-1]

	def __str__(self) :
		return self.header

	def __hash__(self) :
		return hash(self.parseHeader())
	def __eq__(self, other) :
		if other.__class__ == self.__class__ :
			return (self.parseHeader() == other.parseHeader())
		else :
			return False

	def __lt__(self, other) :
		return self.header < other.header

	def __ne__(self, other) :
		return (self.parseHeader() != other.parseHeader())

	def getGenus(self) :
		return self.parseHeader().split(' ')[0]

	def getSpecies(self) :
		name = self.parseHeader().split(' ')
		sp = ''
		if len(name) > 1 :
			sp = name[1]
		return sp

isAligned = True
# This will see if the data are aligned, then set a global variable
def checkAlignment(data) :
	global isAligned
	length = len((list(data.values())[0][0]).seq)
	for header in data :
		for gene in data[header] :
			if len(gene.seq) != length :
				isAligned = False
				return False
	return isAligned

def put_in_map(gene, key, map) :
	if key == '' :
		printdebug('Blank key for %s' %gene.name)
		return
	if key not in map :
		map[key] = []
	map[key].append(gene)

def parse_input(filename) :
	in_file = open(filename, 'r')
	print ("Parsing input.")
	header = Header('')
	header_map= {}
	genus_map = {}
	species_map = {}
	for line in in_file :
		line = line.strip()
		if line == '' :
			continue
		if line[0] == '>' :
			if header.header != '' :
				#data[header].append(Gene(header, seq))
				put_in_map(Gene(header, seq), header, header_map)
				put_in_map(Gene(header, seq), header.getGenus(), genus_map)
				put_in_map(Gene(header, seq), header.getSpecies(), species_map)
			header = Header(line)
			seq = ''
		else :
			seq += line
	# Take care of the last sequence in the file
	put_in_map(Gene(header, seq), header, header_map)
	put_in_map(Gene(header, seq), header.getGenus(), genus_map)
	put_in_map(Gene(header, seq), header.getSpecies(), species_map)
	in_file.close()
	checkAlignment(header_map)
	return species_map, genus_map, header_map

nucs = ['A', 'T', 'C', 'G', 'a', 't', 'c', 'g']
def calc_nuc_percent(seq, length) :
	global isAligned
	global nucs
	count = 0
	for char in seq :
		if char in nucs :
			count += 1
	result = 1.0 * count
	if isAligned :
		result = (1.0 * count) / length
	return result

# This puts the best sequence at index 0 of the list (argument data map goes from header to list of Gene)
# It returns a map from Header to Gene
def remove_duplicates(data, length) :
	num_pattern = re.compile('[0-9]+')
	for header in data :
		seq_genes = data[header]
		size = len(seq_genes)
		best_percent = 0.0
		best_index = -1
		for i in range(0, size) :
			percent = calc_nuc_percent(seq_genes[i].seq, length)
	#		printdebug('%s\t%.2f' %(seq_genes[i].name.header, percent))
			if percent > best_percent :
		#		printdebug('%.2f > %.2f\t%s' %(percent, best_percent, header))
				best_percent = percent
				best_index = i
			elif percent == best_percent :
				printdebug('%.2f == %.2f\t%s\t%s' %(percent, best_percent, seq_genes[i].name.header, seq_genes[best_index].name.header))
				# Prefer the result with no number in the header
				if not num_pattern.search(seq_genes[i].name.header) and num_pattern.search(seq_genes[best_index].name.header) :
					best_percent = percent
					best_index = i
				# Take the alphabetically lower name otherwise (this is just to make sure we get unique output)
				elif seq_genes[i].name.header < seq_genes[best_index].name.header :
					best_percent = percent
					best_index = i
		best_gene = seq_genes[best_index]
		best_gene.remove_number()
		# The map no longer goes to a list, but just to a gene object
		data[header] = best_gene
	return data

def write_data(ofile, seq_gene) :
	# name is a Header object, but I overrode the __str__ method, so this works just fine.
	ofile.write('%s\n' %seq_gene.name)
	seq_out = ''
	i = 0
	for char in seq_gene.seq :
		if i % 60 == 0 :
			seq_out = seq_out + '\n'
		seq_out = seq_out + char
		i += 1
	# This takes care of whitespace at beginning and end of string
	seq_out = seq_out.strip()
	ofile.write('%s\n' %seq_out)

def write_output(filename, data) :
	ofile = open(filename, 'w')
	for header in sorted(data) :
		write_data(ofile, data[header])
	ofile.close()

the_nucs = ['A','T','G','C','a','t','g','c']
the_dump = ['N','n','-','?']
def is_garbage(genes, pos) :
	global the_dump
	result = True
	for gene in genes :
		if gene.seq[pos] not in the_dump :
			result = False
			break
	return result

def str_minus_index(str, pos) :
	global the_nucs
	#printdebug('Before:\t%s' %str)
	arr = list(str)
	char = arr.pop(pos)
	if char in the_nucs :
		print('ERROR: Huge error! The char %s was removed from a line.' %char)
	#printdebug('After:\t%s' %(''.join(arr)))
	return ''.join(arr)

def remove_column(genes, pos) :
	for gene in genes :
		before = len(gene.seq)
		gene.seq = str_minus_index(gene.seq, pos)
		if len(gene.seq) != before - 1 :
			print('ERROR: Huge error in removing columns! Before: %d After: %d' %(before, len(gene.seq)))
	return genes

def reconstruct_map(genes) :
	data = {}
	for gene in genes :
		data[gene.name] = gene
	return data

def lengths_are_equal(genes) :
	size = len(genes[0].seq)
	for gene in genes :
		if len(gene.seq) != size :
			return False
	return True

# Assume that at this point, data has no duplicates
# genes should be an array of Gene objects
def remove_garbage_columns(genes) :
	global simple
	if not lengths_are_equal(genes) :
		print('ERROR: I don\'t think this input file is aligned! The sequence lengths are different!')
		if not simple :
			print('Script will still run to completion. Output will not be aligned, and no columns will be removed.')
			print('Note that the output is affected in the following way:')
			print('\tThe sequences with the most number of nucleotides are kept (not the highest percentage.)')
			return reconstruct_map(genes)
		else :
			print('You will get no meaningful output, because simple mode requires an aligned input.')
			return genes
	size = len(genes[0].seq)
	i = 0
	while i < size :
		if is_garbage(genes, i) :
			printdebug('Garbage at %d' %i)
			genes = remove_column(genes, i)
			i -= 1
			size = len(genes[0].seq)
		i += 1
	if simple :
		return genes
	return reconstruct_map(genes)

#def export_headers_with_numbers(filename) :
	# NOTE: Be careful with this: because shell=True, shell commands will execute.
	# I tried to protect you with quotes around the filename variable.
	#subprocess.call('egrep \'[0-9]+\' \'%s\' > \'%s_numbered_headers.txt\'' %(filename, filename), shell=True)

def runReduce(data, ofname) :
	global isAligned
	length = len((list(data.values())[0][0]).seq)
	if isAligned :
		printdebug('Alignment length is: %d' %length)
	data = remove_duplicates(data, length)
	data = remove_garbage_columns(list(data.values()))
	print ("Writing output")
	write_output(ofname, data)
#	export_headers_with_numbers(ofname)
	print('Done writing.')
	return data

def run_simple(input_file, data) :
	vals = list(data.values())
	genes = []
	for array in vals :
		for gene in array :
			genes.append(gene)
	genes = remove_garbage_columns(genes)
	out_name = "%s_cleaned.fasta" %input_file.split('.')[0]
	of = open(out_name, 'w')
	for gene in genes :
		write_data(of, gene)
	of.close()

def handle_args(args) :
	global debugging
	global simple
	parser = argparse.ArgumentParser()
	parser.add_argument('input', help='Provide a location to alignment file.')
	parser.add_argument('--debug', help='This makes extra stuff print out for the debugger\'s benefit.', action='store_true')
	parser.add_argument('--simple', help='This gives only one output, chopping the columns of garbage.', action='store_true')
	args = parser.parse_args()
	input = args.input
	print('Using input: %s' %input)
	debugging = args.debug
	printdebug('If you see this message, you are a developer. Congrats. Your terminal will soon be full of meaningful junk.')
	simple = args.simple
	return input

def main(args) :
	input_file = handle_args(args)
	print_info()
	# data is a map from header to header-seq gene objects
	species_map, genus_map, header_map  = parse_input(input_file)

	global simple
	if simple :
		print('Running a simple version of the program.')
		print('Output gives only one output, chopping the columns of garbage.')
		run_simple(input_file, header_map)
		return 0

	print ("\nSelecting best duplicate species.")
	ofname1 = "%s_best_in_species.fasta" %input_file.split('.')[0]
	species_map = runReduce(species_map, ofname1)

	print ("\nSelecting best duplicate genus.")
	ofname2 = "%s_best_in_genus.fasta" %input_file.split('.')[0]
	genus_map = runReduce(genus_map, ofname2)
	return 0

if __name__ == "__main__" :
	main(sys.argv)
	print('Done.')

