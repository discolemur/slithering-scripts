#! /bin/bash


if ! [ -e Aliscore.02.2.pl ]
then
    cp /fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore.02.2.pl ./
fi

if ! [ -e Aliscore_module.pm ]
then
    cp /fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore_module.pm ./
fi

for file in *.aln
do
    batch="$file"Batch.sh
    if [ -e $batch ]
    then
        continue
    fi
    echo '#!/bin/bash' > $batch
    echo '#SBATCH --time=0:15 --ntasks=1 --nodes=1 --mem-per-cpu=500M -J Ali' >> $batch
    echo '' >> $batch
    echo "perl Aliscore.02.2.pl -i $file" >> $batch
#    sbatch $batch
done

