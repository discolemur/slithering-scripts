#! /bin/env python

# This script removes all '-' characters from a fasta file

import sys
import shutil

def main(args) :
	if len(args) != 2 :
		print("Usage: %s <fasta>" %args[0])
		return 1
	file = open(args[1], 'r')
	tmp = 'tmp_aln_for_script'
	out = open(tmp, 'w')
	for line in file :
		if line[0] == '>' :
			out.write(line)
		else :
			data = ''
			for char in line :
				if char != '-' :
					data = data + char
			out.write(data)
	out.close()
	file.close()
	shutil.move(tmp, args[1])
	return 0

if __name__ == "__main__" :
	main(sys.argv)
