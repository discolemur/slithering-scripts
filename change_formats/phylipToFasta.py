#! /usr/bin/env python

import sys
from Bio import SeqIO

# Converts phylip to fasta. Python 3 does not work with this on marylou (currently) because biopython is only installed in python 2

def main(args) :
    if (len(args) != 3) :
        print("Gimme an input and output file next time.\n")
        print("Usage: %s <input.phy> <output.fasta>\n" %args[0])
        return 1
    SeqIO.convert(args[1], "phylip", args[2], "fasta")

if __name__ == "__main__" :
    main(sys.argv)

