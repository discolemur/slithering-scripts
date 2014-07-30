#! /bin/env python

import sys
import re

def print_info() :
	print ""
	print "This script takes one argument (fasta alignment) and does the following:"
	print ""
	print " Output 1 (saved in FILENAME_no_duplicates.fasta)"
	print "\tIf any duplicates exist for a species, it picks the one with the most nucleotide [ATGCatgc] data"
	print "\tThis output file has exactly one sequence per species"
	print ""
	print " Output 2 (saved in FILENAME_best_in_genus.fasta"
	print "\tOut of all species in a genus, it picks the one with the most nucleotide data"
	print "\tThis output file has exactly one sequence per genus (from the species with the most data)"
	print ""

nucs = ['A', 'T', 'C', 'G', 'a', 't', 'c', 'g']
def calc_nuc_percent(seq, length) :
	global nucs
	count = 0
	for char in seq :
		if char in nucs :
			count += 1
	return (1.0 * count) / length

def parse_header(line) :
	original = line
	line = line[1:]
	line = line.split('_')
	if len(line) < 2 :
		print "(This is probably not an error) Did not find a species for genus in line : %s" %original
		species = ''
	else :
		species = line[1]
		species = re.sub(r'[^a-zA-Z]', '', species)
	genus = line[0]
	return "%s %s" %(genus, species)

def parse_input(in_file, data) :
	name = ''
	for line in in_file :
		line = line.strip()
		if line[0] == '>' :
			if name != '' :
				if name not in data :
					data[name] = []
				data[name].append(seq)
			name = parse_header(line)
			seq = ''
		else :
			seq += line
	return data

def remove_duplicates(data, length) :
	for name in data :
		seqs = data[name]
		size = len(seqs)
		best_percent = 0
		best_index = -1
		for i in range(0, size) :
			percent = calc_nuc_percent(seqs[i], length)
			if percent > best_percent :
				best_index = i
		best_seq = seqs[best_index]
		data[name] = [best_seq]
	return data

def get_seq_length(seq) :
	i = 0
	for char in seq: 
		i += 1
	return i

def contains_duplicates(data) :
	for name in data :
		array = data[name]
		if len(array) != 1 :
			return True
	return False

def write_output(filename, data) :
	out_file = open(filename, 'w')
	for name in data :
		out_file.write('>%s\n' %name)
		seq = data[name][0]
		seq_out = ''
		i = 0
		for char in seq :
			if i % 60 == 0 :
				seq_out = seq_out + '\n'
			seq_out = seq_out + char
			i += 1
		if seq_out[0] == '\n' :
			seq_out = seq_out[1:]
		seq_out.strip()
		out_file.write('%s\n' %seq_out)
	out_file.close()

def add_to_genus(best_name, best_seq, by_genus) :
	if best_name == '' or best_seq == '' :
		print "If anything appears after the colon, there may be an error: %s %s" %(best_name, best_seq)
	else :
		by_genus[best_name] = [best_seq]
	return by_genus


class Pair(object) :
	def __init__(self, name, seq) :
		self.name = name
		self.seq = seq


def map_from_genus(data) :
	from_genus = {}
	prev = ''
	for name in data :
		genus = name.split(' ')[0]
		seq = data[name][0]
		if genus == '' :
			genus = name.split(' ')[1]
		if genus != prev :
			if genus not in from_genus :
				from_genus[genus] = []
			prev = genus
		from_genus[genus].append(Pair(name, seq))
	return from_genus

def collapse_genus(genus_map, length) :
	data = {}
	for genus in genus_map :
		best_name = ''
		best_seq = ''
		best_per = 0.0
		for pair in genus_map[genus] :
			percent = calc_nuc_percent(pair.seq, length)
			if percent > best_per :
				best_per = percent
				best_name = pair.name
				best_seq = pair.seq
		if best_seq == '' or best_name == '' and genus != '' :
			print "Possible error, something is blank for name, seq: %s, %s" %(best_name, best_seq)
			print "Genus %s has no output." %genus
		data[best_name] = [best_seq]
	return data

def main(args) :
	print_info()
	if len(args) != 2 :
		print "INCORRECT ARGUMENTS"
		print "Usage: %s <alignment_file.fasta>"
		return 1
	# data is a map from name (format: "Genus species") to sequence
	data = {}
	in_file = open(args[1], 'r')
	print "Parsing input."
	data = parse_input(in_file, data)
	in_file.close()
	length = get_seq_length(data[data.keys()[0]][0])
	print "Selecting best duplicates."
	data = remove_duplicates(data, length)
	if contains_duplicates(data) :
		print "ERROR: Duplicates remain!"
	print "Writing output 1"
	out_name = "%s_no_duplicates.fasta" %args[1].split('.')[0]
	write_output(out_name, data)
	print "Collapsing to one species per genus."
	genus_map = map_from_genus(data)
	data = collapse_genus(genus_map, length)
	print "Writing output 2"
	out_name = "%s_best_in_genus.fasta" %args[1].split('.')[0]
	write_output(out_name, data)

if __name__ == "__main__" :
	main(sys.argv)

