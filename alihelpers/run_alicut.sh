#! /bin/bash

echo 's' | ALICUT_V2.3.pl

for file in *.aln
do
	if ! [ -e ALICUT_$file ]
	then
		cp $file ALICUT_$file
	fi
done
