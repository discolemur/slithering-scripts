# This script takes two arguments:
#     $1 = location/input.fasta
#     $2 = location/output.gff

# Program locations:
TransDecoder=/fslgroup/fslg_BybeeLab/software/trinityrnaseq_r20131110/trinity-plugins/TransDecoder_r20131110/TransDecoder

# If this script runs multiple times, it needs its own directory for its own stuff.
# The tmp directory is named from the second input parameter
name=${2##*/}_tmp
mkdir $name
cp $1 $name/Trinity.fasta
cd $name

fasta_file=Trinity.fasta

# Step 1.2 : run TransDecoder on fasta files to obtain peptide sequences ([file_name].pep)
$TransDecoder -t $fasta_file
