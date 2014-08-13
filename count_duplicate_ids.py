#! /bin/env python

import sys
import glob
import os

verbose = True

def parse_header(line) :
	if len(line.split('.')) == 1 :
		return line[1:]
	return line[1:].split('.')[1].split('|')[0]

def handle_file(file) :
	global verbose
	input = open(file, 'r')
	ids = {}
	counter = 0
	for line in input :
		line = line.strip()
		if line[0] == '>' :
			id = parse_header(line)
			if id in ids :
				ids[id] += 1
				counter += 1
			else :
				ids[id] = 1
	print('%d duplicate ids in %s' %(counter, file))
	for id in ids :
		if ids[id] > 1 :
			if not verbose :
				print('%s: %d' %(id, ids[id]))
	if os.path.isfile(file + '_mod') :
		mod_counter = handle_file(file + '_mod')
		print('\t%d removed for %s' %((counter - mod_counter), file))
	return(counter)

files = glob.glob('*.pep')
for file in files :
	handle_file(file)
