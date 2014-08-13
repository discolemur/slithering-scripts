#! /bin/env python

import sys

def is_fasta_sorted(filename) :
	in_file = open(filename, 'r')
	header = ''
	for line in in_file :
		if line[0] == '>' :
			if header == '' :
				header = line
			elif line >= header :
				header = line
			else :
				print('Prev: %s' %header)
				print('Next: %s' %line)
				return False
	return True

def main(args) :
	if len(args) != 2 :
		print('Usage: %s <file.fasta>' %args[0])
		return 1
	print(is_fasta_sorted(args[1]))
	return 0

if __name__ == '__main__' :
	main(sys.argv)
