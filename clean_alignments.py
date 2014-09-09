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
	print('\tOutput is in aligned fasta format. Once organisms have been removed,')
	print('\tall resulting empty columns (places where every sequence has -, ?, n, or N)')
	print('\tare removed, so the alignments are clean and trimmed.')
	print('')

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
		for pair in data[header] :
			if len(pair.seq) != length :
				isAligned = False
				return

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
	checkAlignment(data)
	return data

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
		result = count / length
	return result

# This puts the best sequence at index 0 of the list (argument data map goes from header to list of Pair sequences)
# It returns a map from Header to Pair
def remove_duplicates(data, length) :
	num_pattern = re.compile('[0-9]+')
	for header in data :
		seq_pairs = data[header]
		size = len(seq_pairs)
		best_percent = 0.0
		best_index = -1
		for i in range(0, size) :
			percent = calc_nuc_percent(seq_pairs[i].seq, length)
			printdebug('%s\t%d' %(seq_pairs[i].name.header, percent))
			if percent > best_percent :
		#		printdebug('%.2f > %.2f\t%s' %(percent, best_percent, header))
				best_percent = percent
				best_index = i
			elif percent == best_percent :
				printdebug('%.2f == %.2f\t%s\t%s' %(percent, best_percent, seq_pairs[i].name.header, seq_pairs[best_index].name.header))
				# Prefer the result with no number in the header
				if not num_pattern.search(seq_pairs[i].name.header) and num_pattern.search(seq_pairs[best_index].name.header) :
					best_percent = percent
					best_index = i
				# Take the alphabetically lower name otherwise (this is just to make sure we get unique output)
				elif seq_pairs[i].name.header < seq_pairs[best_index].name.header :
					best_percent = percent
					best_index = i
		best_pair = seq_pairs[best_index]
		# The map no longer goes to a list, but just to a pair object
		data[header] = best_pair
	return data

def write_data(ofile, seq_pair) :
	# name is a Header object, but I overrode the __str__ method, so this works just fine.
	ofile.write('%s\n' %seq_pair.name)
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
	for header in sorted(data) :
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

the_nucs = ['A','T','G','C','a','t','g','c']
the_dump = ['N','n','-','?']
def is_garbage(pairs, pos) :
	#global the_dump
	global the_nucs
	result = True
	for pair in pairs :
		#if pair.seq[pos] not in the_dump :
		if pair.seq[pos] in the_nucs :
			result = False
			break
	return result

def str_minus_index(str, pos) :
	arr = list(str)
	arr.pop(pos)
	return ''.join(arr)

def remove_column(pairs, pos) :
	for pair in pairs :
		pair.seq = str_minus_index(pair.seq, pos)
	return pairs

def reconstruct_map(pairs) :
	data = {}
	for pair in pairs :
		data[pair.name] = pair
	return data

def lengths_are_equal(pairs) :
	size = len(pairs[0].seq)
	for pair in pairs :
		if len(pair.seq) != size :
			return False
	return True

# Assume that at this point, data has no duplicates
# pairs should be an array of Pair objects
def remove_garbage_columns(pairs) :
	global simple
	if not lengths_are_equal(pairs) :
		print('WHOA! I don\'t think this input file is aligned! The sequence lengths are different!')
		if not simple :
			print('Script will still run to completion. Output will not be aligned, and no columns will be removed.')
			print('Note that the output is affected in the following way:')
			print('\tThe sequences with the most number of nucleotides are kept (not the highest percentage.)')
			return reconstruct_map(pairs)
		else :
			print('You will get no meaningful output, because simple mode requires an aligned input.')
			return pairs
	size = len(pairs[0].seq)
	i = 0
	while i < size :
		if is_garbage(pairs, i) :
			printdebug('Garbage at %d' %i)
			pairs = remove_column(pairs, i)
			i -= 1
			size = len(pairs[0].seq)
		i += 1
	if simple :
		return pairs
	return reconstruct_map(pairs)

def export_headers_with_numbers(filename) :
	# NOTE: Be careful with this: because shell=True, shell commands will execute.
	# I tried to protect you with quotes around the filename variable.
	subprocess.call('egrep \'[0-9]+\' \'%s\' > \'%s_numbered_headers.txt\'' %(filename, filename), shell=True)

def runReduce(data, ofname) :
	global isAligned
	length = len((list(data.values())[0][0]).seq)
	if isAligned :
		printdebug('Alignment length is: %d' %length)
	data = remove_duplicates(data, length)
	data = remove_garbage_columns(list(data.values()))
	print ("Writing output")
	write_output(ofname, data)
	export_headers_with_numbers(ofname)
	print('Done writing.')
	return data

def run_part_1(input_file, data) :
	print ("\nSelecting best duplicates.")
	ofname1 = "%s_best_in_species.fasta" %input_file.split('.')[0]
	data = runReduce(data, ofname1)
	return data

def run_part_2(input_file, data) :
	print ("\nCollapsing to one species per genus.")
	ofname2 = "%s_best_in_genus.fasta" %input_file.split('.')[0]
	genus_map = map_from_genus(data)
	data = runReduce(genus_map, ofname2)
	return data

def run_simple(input_file, data) :
	vals = list(data.values())
	pairs = []
	for array in vals :
		for pair in array :
			pairs.append(pair)
	pairs = remove_garbage_columns(pairs)
	out_name = "%s_cleaned.fasta" %input_file.split('.')[0]
	of = open(out_name, 'w')
	for pair in pairs :
		write_data(of, pair)
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
	# data is a map from header to header-seq pair objects
	data = parse_input(input_file, {})
	global simple
	if simple :
		print('Running a simple version of the program.')
		print('Output gives only one output, chopping the columns of garbage.')
		run_simple(input_file, data)
		return 0
	data = run_part_1(input_file, data)
	run_part_2(input_file, data)
	return 0

if __name__ == "__main__" :
	main(sys.argv)
	print('Done.')

