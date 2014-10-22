#! /usr/bin/env python

import glob
import subprocess
import os

def trim_file(filename, trimmed_fasta) :
	fh = open('tmp%s' %filename, 'w')
	for header in trimmed_fasta :
		fh.write('%s\n%s\n' %(header, trimmed_fasta[header]))
	fh.close()
	subprocess.call('mafft tmp%s > %s' %(filename, filename), shell=True)
	os.remove('tmp%s' %filename)

def handle_file(file) :
	fasta = {}
	header = ''
	fh = open(file, 'r')
	for line in fh :
		line = line.strip()
		if line[0] == '>' :
			header = line
			fasta[header] = ''
		else :
			fasta[header] += line.replace('-', '')
	fh.close()
	good = True
	fasta_keys = list(fasta.keys())
	for header in fasta_keys :
		if len(fasta[header]) == 0 :
			del fasta[header]
			good = False
	if not good :
		print('bad %s' %file)
#		trim_file(file, fasta)

def main() :
	files = glob.glob('*.aln')
	for file in files :
		handle_file(file)

if __name__=='__main__' :
	main()
