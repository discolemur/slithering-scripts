#! /bin/bash

for item in *.aln
do
	if [ -e $item.sh -o -e $item.iqtree ]
	then
		echo "$item iqtree was already run, or the batch script already exists."
		continue
	fi

	echo '#!/bin/bash' > $item.sh
	echo '' >> $item.sh
	echo '#SBATCH --time=3:00:00   # walltime' >> $item.sh
	echo '#SBATCH --ntasks=8   # number of processor cores (i.e. tasks)' >> $item.sh
#	echo '#SBATCH --nodes=1   # number of nodes' >> $item.sh
	echo '#SBATCH --mem-per-cpu=2G   # memory per CPU core' >> $item.sh
	echo "#SBATCH -J iqtree_$item   # job name" >> $item.sh
	echo '' >> $item.sh
#	echo "/fslhome/njensen6/software/bin/iqtree-omp -omp 8 -m TEST -s $item" >> $item.sh
	echo "/fslhome/njensen6/software/bin/iqtree-omp -omp 8 -m TEST -wsl -wt -b 1 -s $item" >> $item.sh

#	sbatch $item.sh

done
