#! /bin/bash

# Produce a script for each inparanoid run to run all inparanoid

function create_script () 
{
	file="$1"
	taxon="${1%%.*}"
	echo "#!/bin/bash" > $file.sh
        echo "" >> $file.sh
        echo "#SBATCH --time=120:00:00   # walltime" >> $file.sh
        echo "#SBATCH --ntasks=1   # number of processor cores (i.e. tasks)" >> $file.sh
        echo "#SBATCH --nodes=1   # number of nodes" >> $file.sh
        echo "#SBATCH --mem-per-cpu=2G   # memory per CPU core" >> $file.sh
        echo "#SBATCH -J hamstr_$file   # job name" >> $file.sh
        echo "#SBATCH --mail-user=nick.j.g12@gmail.com   # email address" >> $file.sh
        echo "#SBATCH --mail-type=FAIL" >> $file.sh
        echo "#SBATCH -o slurm_output_$file.txt" >> $file.sh
        echo "#SBATCH -e slurm_error_$file.err" >> $file.sh
        echo "" >> $file.sh
	echo "../bin/hamstr -sequence_file=$file -taxon=$taxon -hmmset=orthodb_extracts -refspec=AMELL" >> $file.sh
}

for file in *.pep
do
	create_script $file
done
