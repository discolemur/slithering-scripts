#! /bin/bash

for file in *.gff
do
	# Remove all extensions
	name="${file%%.*}"
	# Print name for fun
	echo $name
	# Rename with new extension
	mv $file $name.gff
done
