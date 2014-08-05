#! /bin/bash

mkdir -p aln_files

for file in *.fa*
do
	mafft $file > aln_files/$file
done

