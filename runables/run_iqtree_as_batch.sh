#! /bin/bash

# This script goes one directory deep, creates super.fasta if not exists, and runs iqtree as a batch if batch not already exists.

for item in *
do
	if ! [ -d $item ]
	then
		continue
	fi

	if [ -e $item/iqtreeBatch.sh -o -e $item/super.fasta.iqtree ]
	then
		echo "$item iqtree was already run, or the batch script already exists."
		continue
	fi

	echo "Entering $item . . ."
	cd $item

	if ! [ -e super.fasta ]
	then
		echo "    super is being created."
		construct_supermatrix.py
	fi

	if ! [ -e super.fasta ]
	then
		echo "    super could not be created."
		cd ..
		continue
	fi

	echo "    super exists."
	echo '#!/bin/bash' > iqtreeBatch.sh
	echo '' >> iqtreeBatch.sh
	echo '#SBATCH --time=120:00:00   # walltime' >> iqtreeBatch.sh
	echo '#SBATCH --ntasks=32   # number of processor cores (i.e. tasks)' >> iqtreeBatch.sh
	echo '#SBATCH --nodes=1   # number of nodes' >> iqtreeBatch.sh
	echo '#SBATCH --mem-per-cpu=8G   # memory per CPU core' >> iqtreeBatch.sh
	echo "#SBATCH -J "iqtree_$item\_njensen6"   # job name" >> iqtreeBatch.sh
	echo '#SBATCH --mail-user=nick.j.g12@gmail.com   # email address' >> iqtreeBatch.sh
#	echo '#SBATCH --mail-type=BEGIN' >> iqtreeBatch.sh
#	echo '#SBATCH --mail-type=END' >> iqtreeBatch.sh
	echo '#SBATCH --mail-type=FAIL' >> iqtreeBatch.sh
	echo '' >> iqtreeBatch.sh
	echo '/fslhome/njensen6/software/bin/iqtree-omp -omp 32 -bb 1000 -m TEST -s super.fasta' >> iqtreeBatch.sh
	sbatch iqtreeBatch.sh

	cd ..
done
