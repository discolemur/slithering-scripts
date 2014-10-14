#! /usr/bin/env python

import os
import sys
import shutil

__author__='njensen6'

# Input format:
# inst#,    actual, predicted, error, probability distribution
#      1          ?        1:H      +  *1      0     (cluster500_bin2)

def is_interesting(row) :
	if row[2] == '2:NH' :
		return True
	return False

def copy_cluster(infile, in_dir, out_dir) :
	shutil.copy('%s/%s' %(in_dir, infile), '%s/%s' %(out_dir, infile))

def main(infile, in_dir) :
	out_dir = 'interesting_clusters'
	if not os.path.isdir(out_dir) :
		os.mkdir(out_dir)

	lines = [line.strip() for line in open(infile, 'r')]
	rows = [row.split() for row in lines[1:]]
	for row in rows :
		if is_interesting(row) :
			copy_cluster('%s.aln' %row[-1][1:-1], in_dir, out_dir)

if __name__=='__main__' :
	main(sys.argv[1], sys.argv[2])
