#! /bin/env python

import glob
import sys

def is_aln(file) :
	file = file.split('/')[1]
	if len(file.split('_')) == 2 and file[-3:] != 'svg':
		return True
	return False

def get_aliscore(file) :
	in_file = open(file, 'r')
	i = 0
	for line in in_file :
		line = line.strip()
		i += len(line.split(' '))
	in_file.close()
	return i

def get_length(file) :
	in_file = open(file, 'r')
	i = 0
	for line in in_file :
		line = line.strip()
		for char in line :
			i += 1
	in_file.close()
	return i

def get_name(file) :
	print(file)
	return(file.split('/')[1].split('_')[1])
	

def usage() :
	print('I need a directory as an argument')

def main(args) :
	if len(args) != 2 :
		usage()
		return 1
	files = glob.glob('%s/mafft_*' %args[1])
	# Map from name to aliscore and length
	values = {}
	out = open('result_normalized.txt', 'w')
	out.write('Name\tAliscore\tLength\n')
	for file in files :
		if is_aln(file) :
			name = get_name(file)
			length = get_length(file)
			list_file = file + '_List_random.txt'
			ali = get_aliscore(list_file)
			out.write('%s\t%s\t%s\n' %(name, ali, length))
	out.close()
	return 0

if __name__ == '__main__' :
	main(sys.argv)

