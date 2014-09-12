#! /bin/env python

import argparse
import os
import subprocess
import random
import sys
import shutil
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from helpers import do_progress_update

## GLOBALS ##
nowhere = open(os.devnull, 'w')
random.seed()
#############

class Gene(object) :
	def __init__(self, sp, seq) :
		self.sp = sp
		self.seq = seq

class Homolog(object) :
	def __init__(self, best_gene, homolog_gene) :
		self.best = best_gene
		self.second = homolog_gene

class Cluster(object) :
	def __init__(self) :
		self.genes = []

	def add(self, gene) :
		self.genes.append(gene)

	def get_homologs(self) :
		homologs = []
		for i in range(0, len(self.genes)) :
			for j in range(i + 1, len(self.genes)) :
				homologs.append(Homolog(self.genes[i], self.genes[j]))
		return homologs

	def get_random_gene(self) :
		return random.choice(self.genes)

def copy_ali_scripts() :
	if not os.path.isfile('Aliscore.02.2.pl') :
		shutil.copyfile('/fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore.02.2.pl', 'Aliscore.02.2.pl')
	if not os.path.isfile('Aliscore_module.pm') :
		shutil.copyfile('/fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore_module.pm', 'Aliscore_module.pm')

def run_aliscore(filename, counter) :
	copy_ali_scripts()
	with open('aliBatch%d.sh' %(counter),'w') as fh :
		fh.write('#!/bin/bash\n')
		fh.write('#SBATCH --time=50:00:00 --ntasks=1 --nodes=1 --mem-per-cpu=4G -J Ali\n\n')
		fh.write('perl Aliscore.02.2.pl -i %s\n' %filename)
	subprocess.call('sbatch aliBatch%d.sh' %(counter), shell=True)

def write_homolog(homolog, counter) :
	filename = '%d.fa' %(counter)
	of_handle = open(filename, 'w')
	of_handle.write('>%s1\n%s\n' %(homolog.best.sp, homolog.best.seq))
	of_handle.write('>%s2\n%s\n' %(homolog.second.sp, homolog.second.seq))
	of_handle.close()
	new_name = filename[:-3] + '.aln'
	subprocess.call("mafft %s > %s" %(filename, new_name), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
	os.remove(filename)
	run_aliscore(new_name, counter)

def write_amount(arr, dir, count) :
	if len(arr) != count :
		print('Did not find enough sequences. Found: %d Required: %d' %(len(arr), count))
		return
	if not os.path.exists(dir) :
		os.mkdir(dir)
	os.chdir(dir)
	for i in range(0, len(arr)) :
		write_homolog(arr[i], i + 1)
	os.chdir('../')

def give(clusters, cl, sp, seq) :
	if sp != '' and seq != '' and seq != 'Sequence_not_publically_available' :
		if cl not in clusters :
			clusters[cl] = Cluster()
		clusters[cl].add(Gene(sp, seq))
	return clusters

def get_random_pairs(clusters, count) :
	randoms = []
	keys = list(clusters.keys())
	for i in range(0, count) :
		# first and second are clusters
		try :
			first = clusters[random.choice(keys)]
			second = clusters[random.choice(keys)]
			a = first.get_random_gene()
			b = second.get_random_gene()
			randoms.append(Homolog(a, b))
		except :
			print('Exception raised in random choice.')
	return randoms

def get_homolog_pairs(clusters, count) :
	homologs = []
	remainder = list(clusters.values())
	while len(homologs) < count and len(remainder) > 0 :
		num = random.randint(0, len(remainder)-1)
		options = remainder.pop(num).get_homologs()
		i = 0
		while len(homologs) < count and i < len(options) :
			homologs.append(options[i])
	return homologs

# Example header:
# >FBgn0152532 FBpp0179035 B4H052 GL14928 IPR005821 EOG700MNR DPERS
def read_file(filename, count) :
	ifhandle = open(filename, 'r')
	clusters = {}
	prev_cl = ''
	sp = ''
	seq = ''
	cl = ''
	geth = False
	for line in ifhandle :
		line = line.strip()
		if line[0] == '>' :
			if geth :
				clusters = give(clusters, cl, sp, seq)
				geto = False
				prev_cl = ''
			line = line.split(' ')
			sp = line[-1]
			cl = line[-2]
			seq = ''
			if cl == prev_cl :
				# handle homolog
				geth = True
			prev_cl = cl
		else :
			seq += line
	print("Getting %d homolog pairs" %count)
	homologs = get_homolog_pairs(clusters, count)
	print("Got %d homolog pairs" %len(homologs))
	print("Getting %d random pairs" %count)
	randoms = get_random_pairs(clusters, count)
	print("Got %d random pairs" %len(randoms))
	write_amount(homologs, 'orthodb_homologs', count)
	write_amount(randoms, 'orthodb_randoms', count)
	ifhandle.close()

def info() :
	print('\n\tWelcome to Nick\'s Homology Extractor 2014\n')
	print('This script gets homologs and random sequences, puts them inside their own directory, aligns them, and runs aliscore.\n')

def main(args) :
	info()
	if len(args) != 2 :
		print('Usage: %s orthodb_file.fasta' %args[0])
		return 1
	filename = args[1]
	print('Reading %s'%filename)
	count = 1500000
	read_file(filename, count)
	print('Done.')

if __name__ == '__main__' :
	main(sys.argv)

