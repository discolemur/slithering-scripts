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
	echo '#SBATCH --time=30:00   # walltime' >> $item.sh
	echo '#SBATCH --ntasks=8   # number of processor cores (i.e. tasks)' >> $item.sh
	echo '#SBATCH --nodes=1   # number of nodes' >> $item.sh
	echo '#SBATCH --mem-per-cpu=100M   # memory per CPU core' >> $item.sh
	echo "#SBATCH -J iqtree_$item   # job name" >> $item.sh
	echo '' >> $item.sh
	echo "/fslhome/njensen6/software/bin/iqtree-omp -omp 8 -bb 1000 -m TEST -s $item" >> $item.sh

	sbatch $item.sh

done
