#! /usr/bin/env python

import sys
import glob

def is_one_to_one(infile, num_sp) :
	result = True
	seqs = {}
	sp = ''
	for line in open(infile, 'r'):
		if line[0] == '>' :
			if '|' in line :
				sp = line.split('|')[1]
			elif '_' in line :
				sp = line.split('_')[1]
			else :
				print('Couldn\'t parse the species, sorry.')
			if sp in seqs :
				result = False
				break
			seqs[sp] = ''
		else:
			seqs[sp] += line[:-1]
	if len(list(seqs.keys())) != num_sp :
		result = False
	return result

def main(num_sp) :
	files = glob.glob('*.aln')
	if len(files) == 0 :
		files = glob.glob('*.fasta')
	if len(files) == 0 :
		print('No files found.')
		ext = input('What is the file extension to use? (aln, fasta, fa, pep) :')
		files = glob.glob('*%s' %ext)
		if len(files) == 0 :
			print('Sorry, you lose.')
			exit(1)
	for file in files :
		if is_one_to_one(file, num_sp) :
			print(file)
	return 0

if __name__ == '__main__' :
	main(int(sys.argv[1]))

print('Done.')
