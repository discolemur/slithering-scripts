#! /bin/bash

if [ "$#" -ne 2 ]
then
	echo "Usage: $0 <directory containing aln files> <name of directory for msf files>"
	exit
fi

mkdir -p "$2"

for file in $1/*.aln
do
#	echo $file
	name="${file##*/}"
	name="${name%.*}"
	output=$2/$name.msf
	/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts/change_formats/fastaToPfam.py $file $output
done
