#! /bin/env python

import glob
import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update

class Pair(object) :
	# Sequences are strings
	def __init__(self, seq1, seq2) :
		self.seq1 = seq1
		self.seq2 = seq2

	def get_length(self) :
		if len(self.seq1) != len(self.seq2) :
			print('The sequences have different lengths. Are you sure they are aligned?')
		return len(self.seq1)

	def get_flanking_gaps_amt(self) :
		counter = 0
		for i in range(0, len(self.seq1) ) :
			if self.seq1[i] == '-' or self.seq2[i] == '-' :
				counter += 1
			elif self.seq1[i] != '-' and self.seq2[i] != '-' :
				break
		i = len(self.seq2) - 1
		while i > 0 :
			if self.seq1[i] == '-' or self.seq2[i] == '-' :
				counter += 1
			elif self.seq1[i] != '-' and self.seq2[i] != '-' :
				break
			i -= 1
		return counter

def get_aliscore(file) :
	in_file = open(file, 'r')
	i = 0
	for line in in_file :
		line = line.strip()
		i += len(line.split(' '))
	in_file.close()
	return i

def read_file(file) :
	#print(file)
	in_file = open(file, 'r')
	seq1 = ''
	seq2 = ''
	# The switch must be set to true the first time when it sees a header
	using_first = False
	for line in in_file :
		line = line.strip()
		if line[0] == '>' :
			# Set from false to true the first time, true to false the second time
			using_first = not using_first
		else :
			if using_first :
				seq1 = seq1 + line
			else :
				seq2 = seq2 + line
	in_file.close()
	return Pair(seq1, seq2)

def get_name(file) :
	# Remove directory
	file = file.split('/')[1]
	# Remove mafft_ if necessary
	if file[:6] == 'mafft_' :
		file = file.split('_')[1]
	# Remove extension
	return file.split('.')[0]

def handle_file(file, out, result) :
	seqs = read_file(file)
	length = seqs.get_length()
	flanking_gaps = seqs.get_flanking_gaps_amt()
	list_file = file + '_List_random.txt'
	ali = get_aliscore(list_file)
	out.write('%d\t%d\t%d\t%d\t%s\n' %(ali, length, (length - flanking_gaps), (ali - flanking_gaps), result))

def get_aln_files(dir) :
	print('Looking for alignment files...')
	files = glob.glob('%s/*.aln' %dir)
	# This takes care of the files without extensions. We gotta change that script, Anton!
	if len(files) == 0 :
		options = glob.glob('%s/*' %dir)
		for file in options :
			if file.split('/')[1][:6] == 'mafft_' and len(file.split('/')[1].split('.')) == 1 :
				files.append(file)
	print('Found %d alignment files.' %len(files))
	return files

def main(args) :
	homolog_files = get_aln_files('orthodb_homologs')
	randoms_files = get_aln_files('orthodb_randoms')
	out = open('result_%s.txt' %args[1].split('/')[0], 'w')
	out.write('Aliscore\tLength\tLenght-FlankingGaps\tAliscore-FlankingGaps\tOut(H/NH)\n')
	do_progress_update(homolog_files, handle_file, out, 'H')
	do_progress_update(randoms_files, handle_file, out, 'NH')
	out.close()
	return 0

if __name__ == '__main__' :
	main(sys.argv)

