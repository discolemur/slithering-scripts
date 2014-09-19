#! /bin/env python

import sys
import shutil
import glob

def change_header(line) :
	line = line[1:]
	line = line.replace('|', '_')
	line = line.replace(':', '_')
	line = line.replace('(', '_')
	line = line.replace(')', '_')
	return line

def handle_file(file) :
	tmp = '%s.tmp' %file
	input = open(file, 'r')
	out = open(tmp, 'w')
	for line in input :
		line = line.strip()
		if line[0] == '>' :
			out.write('>%s\n' %change_header(line))
		else :
			out.write('%s\n' %line)
	input.close()
	out.close()
	shutil.move(tmp, file)
	return 0

def main(args) :
	files = glob.glob('*.aln')
	for file in files : handle_file(file)

if __name__ == "__main__" :
	main(sys.argv)
