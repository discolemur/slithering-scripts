#! /bin/env python

def info() :
	print('\nThis script pulls files from all fa_dir* directories, takes out the core ortholog sequences,')
	print('then creates a file in a cluster directory, or appends to existing file.\n')
#	print('IMPORTANT: all organism names must have \'assembly\' in it to be identified as experimental data (not orthodb data)')

import sys
import glob
import os
#import re
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update

output_dir = 'multi_clusters'
#matcher = re.compile('.*assembly.*')

def open_output(fname) :
	global output_dir
	output = '%s/%s' %(output_dir, fname)
	if os.path.isfile(output) :
		return open(output, 'a')
	else :
		return open(output, 'w')

def handle_file(fname, dir) :
	global matcher
	fname = fname.split('/')[-1]
	out = open_output(fname)
	input = open('%s/%s' %(dir, fname), 'r')
	getNext = False
	ids = set()
	for line in input :
		if line[0] == '>' :
			id = line.split('|')
			if len(id) > 3 and id[3] not in ids :
					ids.add(id[3])
					out.write(line)
					getNext = True
			else :
				getNext = False
		elif getNext :
			out.write(line)
	input.close()
	out.close()

def handle_dir(dir) :
	print('Handling directory %s with files *.fa' %dir)
	files = glob.glob('%s/*.fa' %dir)
	do_progress_update(files, handle_file, dir)

def make_output_dir() :
	global output_dir
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

def main(args) :
	info()
	if len(args) != 1 :
		print("Usage: %s" %args[0])
		return 1
	make_output_dir()
	dirs = glob.glob('fa_dir*')
	print('Handling directories with name fa_dir*')
	for dir in dirs :
		handle_dir(dir)
		
if __name__ == '__main__' :
	main(sys.argv)
