# This script takes two arguments:
#     $1 = location/input.fasta

# Program locations:
TransDecoder=/fslgroup/fslg_BybeeLab/software/trinityrnaseq_r20131110/trinity-plugins/TransDecoder_r20131110/TransDecoder

# If this script runs multiple times, it needs its own directory for its own stuff.
name=${1##*/}_transdecoder_tmp
mkdir $name
cp $1 $name/
cd $name

# Step 1.2 : run TransDecoder on fasta files to obtain peptide sequences ([file_name].pep)
$TransDecoder -t $1
