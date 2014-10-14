#! /bin/bash

counter=1

# Produce a script to run multiparanoid

file="runMultiparanoid.sh"

echo -n "./multiparanoid.pl -species " > $file

for item in *.pep
do
	# add to multiparanoid file
	if [ $((counter++)) -ne 1 ]
	then
		echo -n "+" >> $file
	fi
	echo -n "$item" >> $file
done

