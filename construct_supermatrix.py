#! /bin/env python

import sys
import re
import glob

# Assume all cluster files are in the directory
# Assume all cluster files begin with the name "cluster"
# Assume the organisms in the clusters always come in the same order

def usage(program_path) :
	print '\nUsage: %s\n' %program_path

# Because all organisms come in order, we can pull headers from any sample file
def produce_headers(sampleFile) :
	superArray = []
	file = open(sampleFile, 'r')
	for line in file :
		if line[0] == '>' :
			line = line.split(' ')
			superArray.append(">%s" %line[-1])
	return superArray

def build_super_matrix(files) :
	total = len(files)
	counter = 0
	percent = total / 10
	if percent == 0 :
		percent = 1
	superArray = produce_headers(files[0])
	num_organisms = len(superArray)
	print "There are %d files." %len(files)
	print "Progress: 0.00%"
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
		if (len(subArray) == 1) :
			print "ERROR: cluster %s gave no output!" %filename
			continue
		if (len(subArray) != num_organisms + 1) :
			print "ERROR: cluster %s has the incorrect number of sequences (%d)." %(filename, len(subArray))
			continue
		for i in range(1, num_organisms + 1) :
			if subArray[i] == "" :
				print "%s has empty sequences." %file
			superArray[i-1] = superArray[i-1] + subArray[i]
		counter += 1
		if counter % percent == 0 :
			print "Progress: %.2f%%" %(counter * 100.0 / total)
	super_file = 'super.fasta'
	superMatrix = open(super_file, 'w')
	for item in superArray :
		superMatrix.write(item)
		superMatrix.write('\n')
	superMatrix.close()
	print 'Output is found in %s' %super_file

# args[1] is the number of organisms
def main(args) :
	if len(args) != 1 :
		usage(args[0])
		exit()
	files = glob.glob("cluster*")
	build_super_matrix(files)

if __name__ == "__main__" :
	main(sys.argv)

