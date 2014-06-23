#! /bin/bash 

mkdir annotations

for file in *.fasta
do
	echo "#!/bin/bash" > $file.sh
	echo "" >> $file.sh
	echo "#SBATCH --time=120:00:00   # walltime" >> $file.sh
	echo "#SBATCH --ntasks=16   # number of processor cores (i.e. tasks)" >> $file.sh
	echo "#SBATCH --nodes=1   # number of nodes" >> $file.sh
	echo "#SBATCH --mem-per-cpu=10G   # memory per CPU core" >> $file.sh
	echo "#SBATCH -J trinotate_$file   # job name" >> $file.sh
	echo "#SBATCH --mail-user=nick.j.g12@gmail.com   # email address" >> $file.sh
	echo "#SBATCH --mail-type=BEGIN" >> $file.sh
	echo "#SBATCH --mail-type=END" >> $file.sh
	echo "#SBATCH --mail-type=FAIL" >> $file.sh
	echo "#SBATCH -o pipeline_output_$file.txt" >> $file.sh
	echo "#SBATCH -e pipeline_error_$file.err" >> $file.sh
	echo "" >> $file.sh
	echo "/fslhome/njensen6/fsl_groups/fslg_BybeeLab/software/trinotate_dependencies/trinotate_minus_trinity.sh ${PWD}/$file $file.gff" >> $file.sh
done

mv *.fasta.sh annotations
