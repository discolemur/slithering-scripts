#! /bin/bash

if [ $# == 0 ]
then
	echo 'You must give a directory to look inside.'
	exit 1
fi

dir=$1

echo 'Before trimming:'
wc -l $dir/left.fastq
echo 'After trimming:'
wc -l $dir/trimmed_1

