#! /bin/env python

import sys
from Bio import AlignIO

def main(args) :
	if (len(args) != 3) :
		print "Gimme an input and output file next time.\n"
		print "Usage: %s <input.fasta> <output.msf>\n" %args[0]
		return 1
	input = open(args[1], 'r')
	output = open(args[2], 'w')
	alns = AlignIO.parse(input, 'fasta')
	AlignIO.write(alns, output, 'stockholm')
	output.close()
	input.close()

if __name__ == "__main__" :
	main(sys.argv)
