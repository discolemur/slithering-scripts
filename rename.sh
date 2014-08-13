#! /bin/bash

for file in *.pep_mod
do
	# Remove all extensions
	name="${file%%.*}"
	# Print name for fun
	echo $name
	# Rename with new extension
	mv $file $name.pep
done
