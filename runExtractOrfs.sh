#! /bin/bash

for dir in *.fasta.gff_tmp
do
	cd $dir
	echo "${dir%%.*}"
	name="${dir%%.*}"
	extractOrfs.py Trinity.fasta.transdecoder.pep Trinity.fasta ../$name.orfs.fasta
	cd ..
done
