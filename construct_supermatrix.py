#! /bin/env python

import sys
import re
import glob

# Assume all cluster files are in the directory
# Assume all cluster files begin with the name "cluster"
# Assume the organisms in the clusters always come in the same order

def usage(program_path) :
	print '\nUsage: %s <number of organisms>\n' %program_path

# Because all organisms come in order, we can pull headers from any sample file
def produce_headers(sampleFile, superArray) :
	file = open(sampleFile, 'r')
	for line in file :
		if line[0] == '>' :
			superArray.append(line)
	return superArray

def build_super_matrix(files, num_organisms) :
	superArray = []
	superArray = produce_headers(files[0], superArray)
	for filename in files :
		file = open(filename, 'r')
		contents = ""
		for line in file :
			if line[0] != '>' :
				line = line.strip()
			contents = contents + line
		file.close()
		p = re.compile(">.*\n")
		subArray = p.split(contents)
		# At this point, subArray[0] is blank
		# the first organism is in subArray[1]
		# etc.
		for i in range(1, num_organisms + 1) :
			superArray[i-1] = superArray[i-1] + subArray[i]
	super_file = 'super.fasta'
	superMatrix = open(super_file, 'w')
	for item in superArray :
		superMatrix.write(item)
		superMatrix.write('\n')
	superMatrix.close()
	print 'Output is found in %s' %super_file

# args[1] is the number of organisms
def main(args) :
	if len(args) != 2 :
		usage(args[0])
		exit()
	num_organisms = int(args[1])
	files = glob.glob("cluster*")
	build_super_matrix(files, num_organisms)

if __name__ == "__main__" :
	main(sys.argv)

