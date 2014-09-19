#! /bin/env python

import argparse
import os
import subprocess
import glob
import random
from numpy.random import poisson
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
	def __lt__(self, other) :
		return self.seq < other.seq
	def to_string(self) :
		return '>%s\n%s\n' %(self.sp, self.seq)

class Homolog(object) :
	def __init__(self, best_gene, homolog_gene) :
		self.best = best_gene
		self.second = homolog_gene
	def __eq__(self, other) :
		return (self.best == other.best and self.second == other.second) or (self.second == other.best and self.best == other.second)
	def __hash__(self) :
		return hash(''.join(sorted([self.best.seq, self.second.seq])))
	def __lt__(self, other) :
		return ''.join(sorted([self.best.seq, self.second.seq])) < ''.join(sorted([other.best.seq, other.second.seq]))


class Cluster(object) :
	def __init__(self) :
		self.genes = {}

	def add(self, gene) :
		# Each additional paralog
		# Will get an extra _ char
		sp = gene.sp
		if sp not in self.genes :
			self.genes[sp] = []
		self.genes[sp].append(gene)

	def get_homologs(self) :
		homolgs = []
		for i in range(0, len(self.genes)) :
			for j in range(i + 1, len(self.genes)) :
				homologs.append(Homolog(self.genes[i], self.genes[j]))
		return homologs

	def get_random_gene(self) :
		key = random.choice(list(self.genes.keys()))
		return random.choice(self.genes[key])

	def size(self) :
		size = 0
		for key in self.genes :
			size += len(self.genes[key])
		return size

	def write(self, of_handle) :
		for key in self.genes :
			for i in range(0, len(self.genes[key])) :
				gene = self.genes[key][i]
				gene.sp = gene.sp + str(i)
				of_handle.write(gene.to_string())

def copy_ali_scripts() :
	if not os.path.isfile('Aliscore.02.2.pl') :
		shutil.copyfile('/fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore.02.2.pl', 'Aliscore.02.2.pl')
	if not os.path.isfile('Aliscore_module.pm') :
		shutil.copyfile('/fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore_module.pm', 'Aliscore_module.pm')

def run_aliscore(filename, counter) :
	copy_ali_scripts()
	with open('aliBatch%d.sh' %(counter),'w') as fh :
		fh.write('#!/bin/bash\n')
		fh.write('#SBATCH --time=00:30 --ntasks=1 --nodes=1 --mem-per-cpu=500M -J Ali\n\n')
		fh.write('perl Aliscore.02.2.pl -i %s\n' %filename)
	#subprocess.call('sbatch aliBatch%d.sh' %(counter), shell=True)
	print('Ready to submit %d' %counter)

def write_cluster(cluster, counter) :
	filename = '%d.fa' %(counter)
	of_handle = open(filename, 'w')
	cluster.write(of_handle)
	of_handle.close()
	new_name = filename[:-3] + '.aln'
	subprocess.call("mafft %s > %s" %(filename, new_name), stdout=nowhere, stderr=subprocess.STDOUT, shell=True)
	os.remove(filename)
	run_aliscore(new_name, counter)

def write_all(arr, dir) :
	if not os.path.exists(dir) :
		os.mkdir(dir)
	os.chdir(dir)
	num_exists = len(glob.glob("*.aln"))
	for i in range(num_exists, len(arr)) :
		write_cluster(arr[i], i + 1)
	os.chdir('../')

def give(clusters, cl, sp, seq) :
	if sp != '' and seq != '' and seq != 'Sequence_not_publically_available' :
		if cl not in clusters :
			clusters[cl] = Cluster()
		clusters[cl].add(Gene(sp, seq))
	return clusters

def get_mean_len(homologs) :
	total = 0.0
	for cl in homologs:
		total += cl.size()
	return total / len(homologs)

def get_random_clusters(homologs) :
	count = len(homologs)
	mean = get_mean_len(homologs)
	lengths = poisson(mean, count)
	randoms = []
	for i in range(0, count) :
		cl = Cluster()
		for j in range(0, lengths[i]) :
			randc = random.choice(homologs)
			randg = randc.get_random_gene()
			cl.add(randg)
		randoms.append(cl)
	return randoms

def get_homolog_clusters(clusters, count) :
	return list(clusters.values())

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
	print("Getting %d homolog clusters" %count)
	homologs = get_homolog_clusters(clusters, count)
	print("Got %d homolog clusters" %len(homologs))
	print("Getting %d random clusters" %len(homologs))
	randoms = get_random_clusters(homologs)
	print("Got %d random clusters" %len(randoms))
	write_all(list(homologs), 'orthodb_homolog_clusters')
	write_all(list(randoms), 'orthodb_random_clusters')
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
	count = 15000
	read_file(filename, count)
	print('Done.')

if __name__ == '__main__' :
	main(sys.argv)

