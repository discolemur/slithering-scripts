#! /usr/bin/env python

import glob

def get_aliscore(alifile) :
	fh = open(alifile, 'r')
	result = 0
	for line in fh :
		line = line.strip()
		if line == '' :
			continue
		result += len(line.split(' '))
	fh.close()
	return result

def get_aln_length(seqfile) :
	result = 0
	fh = open(seqfile, 'r')
	# Read a header line
	header = fh.readline()
	while header[0] != '>' :
		header = fh.readline()
	# We are now definitely at the beginning of a sequence
	for line in fh :
		line = line.strip()
		# Stop at the next header
		if line[0] == '>' :
			break
		# Add the length of the line in the alignment
		result += len(line)
	fh.close()
	num_seqs = 0
	fh = open(seqfile, 'r')
	for line in fh :
		if line[0] == '>' :
			num_seqs += 1
	fh.close()
	return result, num_seqs

def handle_dir(ofhandle, dir, out) :
	files = glob.glob('%s/*List*' %dir)
	for alifile in files :
		seqfile = alifile.split('_List')[0]
		length, num_seqs = get_aln_length(seqfile)
		aliscore = get_aliscore(alifile)
		name = '%s_numseqs%d' %(seqfile.split('.')[0], num_seqs)
		ofhandle.write('%s\t%d\t%d\t%s\n' %(name, length, aliscore, out))

def main() :
	ofhandle = open('experimental_cluster_aliscores.txt', 'w')
	ofhandle.write('id\tlength\taliscore\tout\n')
	handle_dir(ofhandle, 'pep_all_OD-R_EP_01_06', '?')
	#handle_dir(ofhandle, 'orthodb_homolog_clusters', 'H')
	#handle_dir(ofhandle, 'orthodb_random_clusters', 'NH')
	ofhandle.close()

if __name__ == '__main__' :
	main()
