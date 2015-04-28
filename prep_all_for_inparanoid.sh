#! /bin/bash

for file in *
do
	if [ "${file##*.}" == "pep" ]
	then
		prep_fasta_for_inparanoid.py $file $file.prepared
	fi
done

rm *.pep

for file in *.prepared
do
	mv $file "${file%.*}"
done
