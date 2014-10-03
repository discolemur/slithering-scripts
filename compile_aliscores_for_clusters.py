#! /usr/bin/env python

import argparse
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

bps = ['A','T','G','C']
def read_aln(seqfile) :
	global bps
	length = 0
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
		length += len(line)
	fh.close()
	num_seqs = 0
	fh = open(seqfile, 'r')
	gaps = 0
	bases = 0
	for line in fh :
		if line[0] == '>' :
			num_seqs += 1
		else :
			gaps += line.count('-')
			for base in bps :
				bases += line.count(base)
	fh.close()
	return length, num_seqs, gaps, bases

def handle_dir(ofhandle, dir, out) :
	files = glob.glob('%s/*List*' %dir)
	for alifile in files :
		seqfile = alifile.split('_List')[0]
		length, num_seqs, gaps, bases = read_aln(seqfile)
		aliscore = get_aliscore(alifile)
		name = '%s' %(seqfile.split('.')[0].split('/')[-1])
		ofhandle.write('%s\t%d\t%d\t%d\t%d\t%d\t%s\n' %(name, length, aliscore, gaps, bases, num_seqs, out))

def main(dir, homology, output) :
	ofhandle = open(output, 'w')
	ofhandle.write('id\tlength\taliscore\tgaps\tbases\tnum_seqs\tout\n')
	handle_dir(ofhandle, dir, homology)
	ofhandle.close()

if __name__ == '__main__' :
	parser = argparse.ArgumentParser()
	parser.add_argument('dir', help='Directory containing aligned clusters with their *List* aliscore files.')
	parser.add_argument('homology', help='H = homologous, NH = non homologous, ? = unknown homology status')
	parser.add_argument('output', help='Output filename. Output will be a table of stuff, so probably you should use a .txt extention.')
	args = parser.parse_args()
	main(args.dir, args.homology, args.output)

