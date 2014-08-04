#! /bin/bash

for file in *.hmm
do
	# Remove all extensions
	name="${file%%.*}"
	# Print name for fun
	echo $name
	# Rename with new extension
	mv $file $name.msf
done
