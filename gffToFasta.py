#! /bin/env python

import sys

## This program takes the following inputs:
##	[locationsOfOrfs].gff
##	[locationsOfDNASeqs].fasta

## ASSUMPTION:
## The annotations in the gff file come from the output of xlsToGff.py
## which was written for the trinotate pipeline

## It produces a specified output filename containing
## The extracted sequences in fasta format

# This class is a pair object holding integer beginning and end positions
class location(object) :
	begin = 0
	end = 0
	def __init__(self, first, last):
		self.begin = int(first)
		self.end = int(last)

# takes a string in the format of gff annotation, gets the sequence ID from it
def parse_id(str) :
	result = ""
	for char in str :
		if char == '.' or char == ' ' :
			break
		else :
			result = result + char
	return result

# gff is in format:
##contig_id      source  feature start   end     score   strand  frame   attribute
# where attribute contains seq_id first, followed by a period
# Takes gff file, finds sequence locations
# Returns dictionary from sequence ID to to/from pair
def parse_gff(gff_in) :
	IDs = []
	locs = []
	for line in gff_in :
		if line[0] != '#' :
			line = line.strip()
			line = line.split('\t')
			IDs.append(parse_id(line[8]))
			locs.append(location(line[3], line[4]))
	return dict(zip(IDs, locs))

# Takes headers from the fasta file and looks in the dictionary	for positions
# finds the sequences at those positions and writes to file
def grab_and_write_sequences(locations, fasta_in, fasta_out) :
	search = False
	counter = 1
	loc = location(0, 0)
	for line in fasta_in :
		line = line.strip()
		if line[0] == '>' :
			ID = line.split(' ')[0][1:]
			if ID in locations :
				loc = locations[ID]
				fasta_out.write('\n')
				fasta_out.write('>')
				fasta_out.write(ID)
				fasta_out.write('\n')
				search = True
				counter = 1
		elif search and line[0] != '>':
			for char in line :
				if counter >= loc.begin and counter <= loc.end :
					if (char == '>') :
						print "There may be a big phat error in counting base pairs."
					fasta_out.write(char)
				if counter == loc.end :
					search = False
				counter += 1

def usage(program_path) :
	print '\nUsage: %s <locations.gff> <sequences.fasta> <outputfile.fasta>\n' %program_path

def main(args) :
	if len(args) != 4 :
		usage(args[0])
		exit()
	gff_in = open(args[1], 'r')
	locations = parse_gff(gff_in)
	gff_in.close()
	fasta_in = open(args[2], 'r')
	fasta_out = open(args[3], 'w')
	grab_and_write_sequences(locations, fasta_in, fasta_out)
	fasta_in.close()
	fasta_out.close()

if __name__ == "__main__" :
	main(sys.argv)
