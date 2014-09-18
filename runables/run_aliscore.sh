#! /bin/bash

cp /fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore.02.2.pl ./
cp /fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore_module.pm ./

for file in *.aln
do
	echo '#!/bin/bash' > aliBatch.sh
	echo '#SBATCH --time=50:00:00 --ntasks=1 --nodes=1 --mem-per-cpu=4G -J Ali' >> aliBatch.sh
	echo '' >> aliBatch.sh
	echo "perl Aliscore.02.2.pl -i $file" >> aliBatch.sh
#	sbatch aliBatch.sh
done

