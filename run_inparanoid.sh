#! /bin/bash

if [ $# -ne 2 ]
then
	echo 'Died. Incorrect arguments.'
	echo 'ARGS'
	echo '$1 first file to inparanoid'
	echo '$2 second file to inparanoid'
	exit 1
else
	mkdir -p $1-$2
	cd $1-$2
	cp /fslgroup/fslg_BybeeLab/scripts/nick/inparanoid_to_copy/* ./
	cp ../$1 ./
	cp ../$2 ./
	./inparanoid_hardcoded_locations.pl $1 $2
fi
