#! /bin/bash

if [ "$#" -ne 2 ]
then
	echo "Usage: $0 <directory containing aln files> <name of directory for hmm files>"
	exit
fi

mkdir -p "$2"

for file in $1/*.aln
do
#	echo $file
	name="${file##*/}"
	name="${name%.*}"
	output=$2/$name.hmm
	hmmbuild --amino -n $name $output $file
done
