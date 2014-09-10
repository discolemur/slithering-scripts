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
	subprocess.call('sbatch aliBatch%d.sh' %(counter))

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
	if len(arr) < count :
		print('Did not find enough sequences.')
		return
	keepers = random.sample(arr, count)
	if not os.path.exists(dir) :
		os.mkdir(dir)
	os.chdir(dir)
	for i in range(0, count) :
		write_homolog(keepers[i], i + 1)
	os.chdir('../')

def give(arr, prev_gene, sp, seq) :
	if sp != '' and seq != '' and prev_gene.seq != '' and prev_gene.sp != '' and seq != 'Sequence_not_publically_available' and prev_gene.seq != 'Sequence_not_publically_available' :
		arr.append(Homolog(prev_gene, Gene(sp, seq)))
	return arr

def get_random_pairs(homologs) :
	randoms = []
	for i in range(0, len(homologs)) :
		first = random.choice(homologs)
		other = random.choice(homologs)
		a = random.choice([first.best, first.second])
		b = random.choice([other.best, other.second])
		randoms.append(Homolog(a, b))
	return randoms

# Example header:
# >FBgn0152532 FBpp0179035 B4H052 GL14928 IPR005821 EOG700MNR DPERS
def read_file(filename, count) :
	ifhandle = open(filename, 'r')
	homologs = []
	prev_cl = ''
	prev_gene = Gene('','')
	sp = ''
	seq = ''
	cl = ''
	geto = False
	getp = False
	for line in ifhandle :
		line = line.strip()
		if line[0] == '>' :
			if geto :
				homologs = give(homologs, prev_gene, sp, seq)
				geto = False
				prev_cl = ''
			elif getp :
				homologs = give(homologs, prev_gene, sp, seq)
				getp = False
				prev_cl = ''
			prev_gene = Gene(sp, seq)
			line = line.split(' ')
			sp = line[-1]
			cl = line[-2]
			seq = ''
			if cl == prev_cl :
				if sp == prev_gene.sp :
					# handle paralo
					getp = True
				else :
					# handle ortholog
					geto = True
			prev_cl = cl
		else :
			seq += line
	print(len(homologs))
	random_seqs = get_random_pairs(homologs)
	print(len(random_seqs))
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
	count = 15000
	read_file(filename, count)
	print('Done.')

if __name__ == '__main__' :
	main(sys.argv)

