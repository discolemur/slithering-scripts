#! /bin/env python

import argparse

def write_split_line(of_handle, split) :
	size = len(split)
	for i in range(0, size - 1) :
		of_handle.write('%s\t' %split[i])
	of_handle.write('%s\n' %split[size - 1])

def write_output(of_handle, lines) :
	for line in lines :
		write_split_line(of_handle, line)

# >cds.comp10002_c0_seq1|m.12725 comp10002_c0_seq1|g.12725  ORF comp10002_c0_seq1|g.12725 comp10002_c0_seq1|m.12725 type:5prime_partial len:406 (+) comp10002_c0_seq1:3-1220(+)
def parse_header(line) :
        return line[1:].split('.')[1].split('|')[0]

# For each file,
# Search that file for ids in solution.disco
# If id is in solution.disco, add the disco line to lines
def search_files(disco) :
	lines = []
	files = list(disco.keys())
	for file in files :
		print('Searching %s' %file)
		in_handle = open(file, 'r')
		for line in in_handle :
			if line[0] == '>' :
				line = line.strip()
				seq_id = parse_header(line)
				if seq_id in disco[file] :
					lines.append(disco[file][seq_id])
		in_handle.close()
	return sorted(lines)

def handle_input_line(of_handle, line, disco) :
	if line[0] == '#' :
		of_handle.write(line)
	else :
		line = line.strip().split('\t')
		pep = line[1]
		seq_id = line[2]
		if pep not in disco :
			disco[pep] = {}
		disco[pep][seq_id] = line
	return disco

def handle_disco(file) :
	if_handle = open(file, 'r')
	disco_out = '%s_trimmed.disco' %file.split('.')[0]
	of_handle = open(disco_out, 'w')
	disco = {}
	for line in if_handle :
		disco = handle_input_line(of_handle, line, disco)
	lines = search_files(disco)
	write_output(of_handle, lines)
	of_handle.close()
	if_handle.close()
	return True

def main() :
	parser = argparse.ArgumentParser()
	parser.add_argument('input', help='Usually solution.disco or some other disco file.')
	args = parser.parse_args()
	disco_in = args.input
	handle_disco(disco_in)

if __name__ == '__main__' :
	main()
