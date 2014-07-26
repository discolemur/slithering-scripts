#! /bin/env python

import glob
import sys

# Output Format:
#
# cluster1	cluster2	...
# sp1	1432	325253	...
# sp2	326526	436	...
# ...

def usage(name) :
	print "Usage: %s" %name

def get_organisms(file) :
	in_file = open(file, 'r')
	result = []
	for line in in_file :
		line = line.strip()
		if line[0] == '>' :
			result.append(line.split(' ')[1])
	in_file.close()
	print result
	return result

def count_line(line) :
	counter = 0
	for char in line :
		if char != '-' :
			counter += 1
	return counter

def add_data(file, data) :
	in_file = open(file, 'r')
	i = -1
	counter = 0
	for line in in_file :
		line = line.strip()
		if line[0] == '>' :
			if i == len(data) :
				data.append([])
			if i >= 0 :
				data[i].append(counter)
			counter = 0
			i += 1
		else :
			counter += count_line(line)
	if i == len(data) :
		data.append([])
	data[i].append(counter)
	in_file.close()
	return data

def main(args) :
	if len(args) != 1 :
		usage(args[0])
		exit()
	files = glob.glob("cluster*")
	organisms = get_organisms(files[0])
	# 2d array
	data = []
	out_file = open("stats_for_clusters", 'w')
	out_file.write('species\t')
	for file in files :
		out_file.write("%s\t" %file.split('.')[0])
		data = add_data(file, data)
	out_file.write('\n')
	i = 0
	for array in data :
		out_file.write('%s\t' %organisms[i])
		i += 1
		for item in array :
			out_file.write('%s\t' %item)
		out_file.write('\n')
	out_file.close()

if __name__ == "__main__" :
	main(sys.argv)

