#! /bin/env python

import glob
import os
import copy
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

	# New proceedure to improve trimming
	# Sliding window begins at ends and removes everything up to the point at which 50% of window size is non-random or non-hyphen
	def trim_by_window(self, ali) :
		win_len = 30
		for i in range(0, len(self.seq1) - win_len) :
			# from left
			self.seq1[i]
		for i in range(0, len(self.seq1) - win_len) :
			# from right
			self.seq1[-i]
		return ali

	def get_flanking_gaps_amt(self, ali) :
		ali_internal = copy.copy(ali)
		ali_internal = trim_by_window(ali_internal)
		counter = 0
		for i in range(0, len(self.seq1) ) :
			if self.seq1[i] == '-' or self.seq2[i] == '-' :
				if str(i + 1) in ali_internal :
					ali_internal.remove(str(i+1))
				counter += 1
			elif self.seq1[i] != '-' and self.seq2[i] != '-' :
				break
		i = len(self.seq2) - 1
		while i > 0 :
			if self.seq1[i] == '-' or self.seq2[i] == '-' :
				if str(i + 1) in ali_internal :
					ali_internal.remove(str(i+1))
				counter += 1
			elif self.seq1[i] != '-' and self.seq2[i] != '-' :
				break
			i -= 1
		return counter, ali_internal

	def __str__(self) :
		return 'First:\n%s\nSecond:\n%s\n' %(self.seq1, self.seq2)

def get_aliscore_list(file) :
	if not os.path.isfile(file) :
		return None
	in_file = open(file, 'r')
	result = []
	for line in in_file :
		line = line.strip().split(' ')
		if len(line) > 0 :
			result += line
	in_file.close()
	return result

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
	if seq1 == '' and seq2 == '' :
		return None
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
	id = file.split('/')[1].split('.')[0] + result
	seqs = read_file(file)
	if seqs is None :
		return
	length = seqs.get_length()
	list_file = file + '_List_random.txt'
	ali = get_aliscore_list(list_file)
	if ali is None :
		return
	flanking_gaps, ali_internal = seqs.get_flanking_gaps_amt(ali)
	if flanking_gaps > length :
		print('ERROR: Flanking gaps is greater than length.')
		print('File: %s\n%s' %(file, seqs))
	out.write('%s\t%d\t%d\t%d\t%d\t%s\n' %(id, len(ali), length, len(ali_internal), (length - flanking_gaps), result))

def get_aln_files(dir) :
	print('Looking for alignment files...')
	files = []
	options = glob.glob('%s/*.aln' %dir)
	for file in options :
		if "ALICUT" not in file :
			files.append(file)
	# This takes care of the files without extensions. We gotta change that script, Anton!
	if len(options) == 0 :
		options = glob.glob('%s/*' %dir)
		for file in options :
			if file.split('/')[1][:6] == 'mafft_' and len(file.split('/')[1].split('.')) == 1 :
				files.append(file)
	print('Found %d alignment files.' %len(files))
	return files

def main() :
	homolog_files = get_aln_files('orthodb_homologs')
	randoms_files = get_aln_files('orthodb_randoms')
	out = open('result_orthodb_table.txt', 'w')
	out.write('ID\tAli\tLen\tAliInternal\tLenInternal\tOut\n')
	do_progress_update(homolog_files, handle_file, out, 'H')
	do_progress_update(randoms_files, handle_file, out, 'NH')
	out.close()
	return 0

if __name__ == '__main__' :
	main()

