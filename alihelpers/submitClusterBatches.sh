#! /bin/bash


function use_dir() {
	counter=1
	cd $dir
	for file in *.aln
	do
		list="$file"_List_random.txt
#		batch=aliBatch"${file%.*}".sh
		batch="$file"Batch.sh
		if ! [ -e $list ]
		then
			if [ $(($counter % 1000)) == 0 ]
			then
				sleep 3m
				cleanClusterBatchDir.sh $dir
			fi
			sbatch $batch
			((counter++))
		fi
	done
	cd ..
}

# Go into cluster directories.
for dir in *clusters
do
	if [ -d $dir ]
	then
		use_dir $dir
	fi
done
