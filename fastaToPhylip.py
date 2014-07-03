#! /bin/env python

import sys
from Bio import SeqIO

def main(args) :
	if (len(args) != 3) :
		print "Gimme an input and output file next time.\n"
		print "Usage: %s <input.fasta> <output.phy>\n" %args[0]
		return 1
	SeqIO.convert(args[1], "fasta", args[2], "phylip")

if __name__ == "__main__" :
	main(sys.argv)
