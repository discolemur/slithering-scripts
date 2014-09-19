#! /bin/bash

cp /fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore.02.2.pl ./
cp /fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore_module.pm ./

for file in *.aln
do
	batch="$file"Batch.sh
	echo '#!/bin/bash' > $batch
	echo '#SBATCH --time=5:00 --ntasks=1 --nodes=1 --mem-per-cpu=8G -J Ali' >> $batch
	echo '' >> $batch
	echo "perl Aliscore.02.2.pl -i $file" >> $batch
	sbatch $batch
done

