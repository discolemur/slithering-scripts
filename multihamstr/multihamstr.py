#! /bin/env python

# This script pulls files from all fa_dir* directories, takes out the core ortholog sequences,
# Then creates a file in a cluster directory, or appends to existing file.

import sys
import glob
import os
import re


output_dir = 'multi_clusters'
matcher = re.compile('.*assembly.*')

def open_output(fname) :
	global output_dir
	output = '%s/%s' %(output_dir, fname)
	if os.path.isfile(output) :
		return open(output, 'a')
	else :
		return open(output, 'w')

def handle(fname, dir) :
	global matcher
	out = open_output(fname)
	input = open('%s/%s' %(dir, fname), 'r')
	getNext = False
	for line in input :
		if line[0] == '>' :
			if matcher.match(line) :
				out.write(line)
				getNext = True
			else :
				getNext = False
		elif getNext :
			out.write(line)
	input.close()
	out.close()

def make_output_dir() :
	global output_dir
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

def main(args) :
	if len(args) != 1 :
		print("Usage: %s" %args[0])
		return 1
	make_output_dir()
	dirs = glob.glob('fa_dir*')
	for dir in dirs :
		files = glob.glob('%s/*' %dir)
		for file in files :
			file = file.split('/')[-1]
			handle(file, dir)

if __name__ == '__main__' :
	main(sys.argv)
