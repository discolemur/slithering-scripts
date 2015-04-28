#! /bin/bash

for file in *.profiles.svg.aln
do
	# Remove all extensions
	name="${file%%.*}"
	# Print name for fun
	echo $name
	# Rename with new extension
	mv $file $name.profiles.svg
done
