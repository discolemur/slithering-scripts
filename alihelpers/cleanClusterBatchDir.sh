#! /bin/bash

dir=$1

cd $dir

# Clean out unused files
rm slurm-*
rm *.svg
rm *Profile_random.txt


# Use all unprocessed files
for file in *.aln
do
	list="$file"_List_random.txt
#	batch=aliBatch"${file%.*}".sh
	batch="$file"Batch.sh
	if [ -e $list -a -e $batch ]
	then
		# Clean out scripts for processed files
		echo "Removing $batch"
		rm $batch
	fi
done
cd ..

