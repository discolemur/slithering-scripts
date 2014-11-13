#! /bin/bash

counter=1

# Produce a script to run multiparanoid

file="runMultiparanoid.sh"

echo -n "./multiparanoid.pl -species " >> $file

for item in *.pep
do
    # add to multiparanoid file
    if [ $((counter++)) -ne 1 ]
    then
        echo -n "+" >> $file
    fi
    echo -n "$item" >> $file
done

# Produce a script for each inparanoid run to run all inparanoid

function create_script () 
{
    file="$1-$2"
    echo "#!/bin/bash" > $file.sh
        echo "" >> $file.sh
        echo "#SBATCH --time=168:00:00   # walltime" >> $file.sh
        echo "#SBATCH --ntasks=1   # number of processor cores (i.e. tasks)" >> $file.sh
        echo "#SBATCH --nodes=1   # number of nodes" >> $file.sh
        echo "#SBATCH --mem-per-cpu=2G   # memory per CPU core" >> $file.sh
        echo "#SBATCH -J stupid_program_$file   # job name" >> $file.sh
        echo "#SBATCH --mail-user=nick.j.g12@gmail.com   # email address" >> $file.sh
        echo "#SBATCH --mail-type=FAIL" >> $file.sh
        echo "#SBATCH -o slurm_output_$file.txt" >> $file.sh
        echo "#SBATCH -e slurm_error_$file.err" >> $file.sh
        echo "" >> $file.sh
    echo "/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts/runables/run_inparanoid.sh $1 $2" >> $file.sh
}

array=(*.fasta)

for (( i=0 ; i < ${#array[@]} ; i++ ))
do
    for (( j=i+1 ; j < ${#array[@]} ; j++ ))
    do
        first="${array[$i]}"
        second="${array[$j]}"
        create_script $first $second
    done
done

