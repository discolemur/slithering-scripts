#! /bin/env python

import glob
import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update

# Example header from transdecoder:
# >cds.comp10002_c0_seq1|m.12725 comp10002_c0_seq1|g.12725  ORF comp10002_c0_seq1|g.12725 comp10002_c0_seq1|m.12725 type:5prime_partial len:406 (+) comp10002_c0_seq1:3-1220(+)
def parse_header(line) :
	return line[1:].split('.')[1].split('|')[0]

def write_output(seqs, filename) :
	outfile = open(filename + '_mod', 'w')
	for seq in seqs :
		outfile.write('%s\n%s\n' %(seqs[seq], seq))
	outfile.close()

def removeDuplicates(filename) :
	file = open(filename, 'r')
	id = ''
	header = ''
	seq = ''
	# map from sequence to header
	seqs = {}
	for line in file :
		line = line.strip()
		if line[0] == '>' :
			if id != '' and seq != '' and header != '':
				if seq not in seqs :
					seqs[seq] = header
				else :
					print('%s is the same as %s' %(id, parse_header(seqs[seq])))
				id = ''
				seq = ''
			id = parse_header(line)
			header = line
			seq = ''
		else :
			if line[-1] == '*' :
				line = line[:-1]
			seq = seq + line
	file.close()
	write_output(seqs, filename)

def main() :
	files = glob.glob("*.pep")
	do_progress_update(files, removeDuplicates)

if __name__ == '__main__' :
	main()
