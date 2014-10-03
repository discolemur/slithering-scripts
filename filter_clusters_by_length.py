#! /usr/bin/env python

import glob
import os
import shutil
import subprocess
import argparse
import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update
import string

nowhere = open(os.devnull, 'w')

class Record(object) :
	def __init__(self, header, seq) :
		self.header = header
		self.seq = seq


log_handle = open('TRIM_LOG', 'w')
def log(msg) :
	global log_handle
	log_handle.write('%s\n' %msg)

def read_file(file) :
	records = []
	header = ''
	seq = ''
	with open(file, 'r') as fh :
		for line in fh :
			line = line.strip()
			if line[0] == '>' :
				if header != '' and seq != '' :
					records.append(Record(header, seq))
				header = line
				seq = ''
			else :
				line = str.replace(line, '-', '')
				seq = seq + line
	if header != '' and seq != '' :
		records.append(Record(header, seq))
	return records

def write_trimmed_file(file, records, dir) :
	global nowhere
	log('trim\t%s' %file)
	with open('tmp.fa', 'w') as fh :
		for record in records :
			fh.write('%s\n%s\n' %(record.header, record.seq))
	new_name = file.split('/')[-1]
	subprocess.call("mafft tmp.fa > \'%s/%s\'" %(dir, new_name), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)	

def copy_existing_file(file, dir) :
	log('copy\t%s' %file)
	shutil.copyfile(file, '%s/%s' %(dir, file.split('/')[-1]))

def handle_file(file, out_dir) :
	with open(file, 'r') as infile :
		records = read_file(file)
		half = max(len(x.seq) for x in records) / 2
		before = len(records)
		records = [elem for elem in records if len(elem.seq) > half]
		after = len(records)
		if before == after :
			copy_existing_file(file, out_dir)
		elif after > 1 :
			write_trimmed_file(file, records, out_dir)

def main(in_dir) :
	out_dir = '%s_trimmed_by_len' %in_dir.split('/')[0]
	if not os.path.exists(out_dir) :
		os.makedirs(out_dir)
	files = glob.glob('%s/*.aln' %in_dir)
	do_progress_update(files, handle_file, out_dir)

if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('dir', help='Directory containing fasta clusters.')
	args = parser.parse_args()
	main(args.dir)
	log('done')
