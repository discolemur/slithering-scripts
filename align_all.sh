#! /bin/bash

mkdir -p aln_files

for file in *.fa*
do
	name="${file%%.*}"
	mafft $file > aln_files/$name.aln
done

