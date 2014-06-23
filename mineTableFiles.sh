#! /bin/bash

location="/fslhome/njensen6/fsl_groups/fslg_BybeeLab/compute/TRANSCRIPTOMES/multiparanoid/InParanoidTables"
echo "Find mined files in: $location"

function is_valid ()
{
	if [ -f $1 -a "${1%%.*}" == "sqltable" ]
	then
		return 0
	else
		return 1
	fi
}

# $1 is function
# $2 is file/folder
function recurse ()
{
	if is_valid $2
	then
		$1 $2
	fi
	if [ -d $2 ]
	then
#		echo "Entering directory: $2"
		cd $2
		for item in *
		do
			recurse $1 $item
		done
		cd ..
	fi
}

# $1 is the item to print
function special_print ()
{
	echo "There's a file here: $1"
}

# $1 is the item to copy
function copy ()
{
	cp $1 $location/
}

for item in *
do
	recurse copy $item
done

