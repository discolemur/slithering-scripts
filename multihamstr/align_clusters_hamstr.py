#! /bin/env python

import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
import glob
import os
import subprocess
from helpers import do_progress_update

nowhere = open(os.devnull, 'w')

def info() :
	print('This program must be run inside a directory of clusters (output from multihamstr.py)')
	print('and puts the clusters (conserved or semi) into their own directory, aligned.')

def is_semiconserved(file, num_sp) :
	file_handle = open(file, 'r')
	species = set()
	result = True
	for line in file_handle :
		if line[0] == '>' :
			sp = line.split('|')[2]
			if sp in species :
				result = False
			species.add(sp)
	file_handle.close()
	return result

def is_conserved(file, num_sp) :
	file_handle = open(file, 'r')
	species = set()
	result = True
	for line in file_handle :
		if line[0] == '>' :
			sp = line.split('|')[2]
			if sp in species :
				result = False
			species.add(sp)
	file_handle.close()
	if len(species) != num_sp :
		result = False
	return result

def has_all_species(file, num_sp) :
	file_handle = open(file, 'r')
	species = set()
	result = True
	for line in file_handle :
		if line[0] == '>' :
			sp = line.split('|')[2]
			species.add(sp)
	file_handle.close()
	if len(species) != num_sp :
		result = False
	return result

def is_valid(file, num_sp, conserve) :
	if conserve :
		return is_conserved(file, num_sp)
	else :
		return is_semiconserved(file, num_sp)

def handle_file(file, num_sp, conserve, dir) :
	global nowhere
	if is_valid(file, num_sp, conserve) :
		new_name = file.split('.')[0] + '.aln'
		subprocess.call("mafft %s > %s/%s" %(file, dir, new_name), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)

def align_files(files, num_sp, conserve) :
	dir = 'conserved_clusters'
	if not conserve :
		dir = 'semiconserved_clusters'
	if not os.path.exists(dir) :
		os.makedirs(dir)
	do_progress_update(files, handle_file, num_sp, conserve, dir)

def complete_clusters(files, num_sp) :
	global nowhere
	dir = 'complete_clusters'
	total = len(files)
	counter = 0
	percent = total / 10
	if not os.path.exists(dir) :
		os.makedirs(dir)
	for file in files :
		counter += 1
		if counter % percent == 0 :
			print("Progress: (%d/%d) %.2f%%" %(counter, total, (1.0 * counter)/total))
		if has_all_species(file, num_sp) :
			new_name = file.split('.')[0] + '.aln'
			subprocess.call("mafft %s > %s/%s" %(file, dir, new_name), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)

def main(args) :
	info()
	if len(args) != 3 or ( args[1] != '-c' and args[1] != '-s' and args[1] != '-a') :
		print('Usage: %s [-c (conserved) or -s (semiconserved) or -a (contains all species, allowing paralogs)] <number of organisms>' %args[0])
		return 1
	files = glob.glob('*.fa')
	if (args[1] == '-a') :
		complete_clusters(files, int(args[2]))
	else :
		conserve = ( args[1] == '-c' )
		align_files(files, int(args[2]), conserve)
	return 0

if __name__ == '__main__' :
	main(sys.argv)
