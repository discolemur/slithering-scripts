#! /bin/env python

import sys

## This program takes the following inputs:
##	[locationsOfOrfs].pep
##	[locationsOfDNASeqs].fasta

## ASSUMPTION:
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

def parse_locs(locs, header) :
	
	locs.append(location(first, last))
	return locs

# Returns dictionary from sequence ID to to/from pair
def parse_pep(pep_in) :
	IDs = []
	locs = []
	for line in pep_in :
		if line[0] == '>' :
			line = line.strip()
			line = line.split(' ')
			line = line[-1]
			line = line.split(':')
			IDs.append(line[0])
			line = line[-1]
			line = line.split('-')
			first = line[0]
			last = line[1].split('(')[0]
			locs.append(location(first, last))
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
						print ("There may be a big phat error in counting base pairs.")
					fasta_out.write(char)
				if counter == loc.end :
					search = False
				counter += 1

def usage(program_path) :
	print ('\nUsage: %s <peptides.pep> <sequences.fasta> <outputfile.fasta>\n' %program_path)

def main(args) :
	if len(args) != 4 :
		usage(args[0])
		exit()
	pep_in = open(args[1], 'r')
	locations = parse_pep(pep_in)
	pep_in.close()
	fasta_in = open(args[2], 'r')
	fasta_out = open(args[3], 'w')
	grab_and_write_sequences(locations, fasta_in, fasta_out)
	fasta_in.close()
	fasta_out.close()

if __name__ == "__main__" :
	main(sys.argv)
