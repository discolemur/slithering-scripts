#! /bin/env python

import sys
import re
import glob

# Assume all cluster files are in the directory
# Assume all cluster files begin with the name "cluster"
# Assume the organisms in the clusters always come in the same order

def usage(program_path) :
	print ('\nUsage: %s\n' %program_path)

# Because all organisms come in order, we can pull headers from any sample file
def produce_headers(sampleFile) :
	headers = []
	file = open(sampleFile, 'r')
	for line in file :
		if line[0] == '>' :
			line = line.strip()[1:]
			line = line.split(' ')
			headers.append(">%s" %line[-1])
	return headers

# files is a list of all cluster files
# headers is a list of header lines for the organisms (organism 1 is in headers[0], etc)
# index is the position of the organism that we are extracting
# num_organisms is the number of organisms total
# superMatrix is the output file (already opened, do not close in this function)
def add_organism_to_matrix(files, headers, index, num_organisms, superMatrix) :
	superMatrix.write(headers[index - 1])
	superMatrix.write('\n')
	for filename in files :
		infile = open(filename, 'r')
		counter = 1
		getting = False
		content = ""
		for line in infile :
			if line[0] == '>' :
				if getting :
					superMatrix.write(content)
					break
				if (counter == index) :
					getting = True
				if counter < 1 or counter > num_organisms :
					print( "Big stinking error, counter: %d" %counter)
					print ("num_organisms: %d" %num_organisms)
					print (line)
				counter += 1
			elif getting :
				line = line.strip()
				content = content + line
		if index == num_organisms :
			superMatrix.write(content)
		infile.close()
	superMatrix.write('\n')

def main(args) :
	if len(args) != 1 :
		usage(args[0])
		exit()
	files = glob.glob("cluster*")
	super_file = 'super.fasta'
	superMatrix = open(super_file, 'w')
	headers = produce_headers(files[0])
	num_organisms = len(headers)
	for index in range(1, num_organisms + 1) :
		add_organism_to_matrix(files, headers, index, num_organisms, superMatrix)
		print ("Progress: %d (%.2f%%)" %(index, index * 100.00 / num_organisms))
	superMatrix.close()
	print ('Output is found in %s' %super_file)

if __name__ == "__main__" :
	main(sys.argv)

