#! /bin/env python

import glob
import shutil

files = glob.glob('sqltable*')


def parse_id(str) :
	if '|' in str :
		str = str.split('|')[0].split('.')[1]
	return str

# input format:
# 1       4901    OD07_Cordulegaster_maculata_A4_assembly.pep     1.000   comp4574_c0_seq2        100%(this element not always here)
# problem format:
# 3653    222     OD07_Cordulegaster_maculata_A4_assembly.pep     1.000   cds.comp1886_c0_seq1|m.1756     100%

for file in files :
	old = file
	new = 'tmp_sqltable'
	in_file = open(old, 'r')
	out_file = open(new, 'w')
	for line in in_file :
		line = line.strip()
		line = line.split('\t')
		id = parse_id(line[4])
		output = '%s\t%s\t%s\t%s\t%s' %(line[0], line[1], line[2], line[3], id)
		if len(line) == 6 :
			output = output + '\t%s\n' %line[5]
		else :
			output = output + '\n'
		out_file.write(output)
	out_file.close()
	in_file.close()
	shutil.move(new, old)
