#! /bin/bash

if [ $# -ne 2 ]
then
	echo "Usage: $0 [-pre or -suf or -re] <prefix or suffix or regex string>"
	exit
fi

use_prefix=-1
prefix="$2"
suffix="$2"
pattern="$2"

if [ $1 == "-pre" ]
then
	use_prefix=1
else
	if [ $1 == "-suf" ]
	then
		use_prefix=0
	else
		if [ $1 == "-re" ]
		then
			use_prefix=-1
		else
			echo "Usage: $0 [-pre or -suf] <prefix or suffix string>"
			exit
		fi
	fi
fi

mkdir mined_files
location="${PWD}/mined_files"
echo "Find mined files in: $location"

# $1 is a file
function is_valid_prefix ()
{
	if [ -f $1 -a "${1%%.*}" == "$prefix" ]
	then
		return 0
	else
		return 1
	fi
}

# $1 is a file
function is_valid_suffix ()
{
	if [ -f $1 -a "${1##*.}" == "$suffix" ]
	then
		return 0
	else
		return 1
	fi
}

function match_pattern()
{
	echo $1 | grep -q "^$pattern"
	if [ -f $1 ]
	then
		if ( echo $1 | grep -q "^$pattern" )
		then
			return 0
		fi
	fi
	return 1
}
# $1 is function to perform on file
# $2 is file/folder
function recurse ()
{
	validity_function=is_valid_suffix
	if [ $use_prefix == 1 ]
	then
		validity_function=is_valid_prefix
	fi
	if [ $use_prefix == -1 ]
	then
		validity_function=match_pattern
	fi

	if $validity_function $2
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
function do_copy ()
{
	cp $1 $location/
}

for item in *
do
	recurse do_copy $item
done


