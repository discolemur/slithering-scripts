# ------------------------Trinotate Pipeline------------------------- #
# ----------------------Minus Trinity Version------------------------ #

# This script takes two arguments:
#     $1 = location/input.fasta
#     $2 = location/output.gff

# Program locations:
TransDecoder=/fslgroup/fslg_BybeeLab/software/trinityrnaseq_r20131110/trinity-plugins/TransDecoder_r20131110/TransDecoder
makeblastdb=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/blast/bin/makeblastdb
blastx=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/blast/bin/blastx
blastp=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/blast/bin/blastp
hmmpress=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/hmmer-3.1b1-linux-intel-x86_64/binaries/hmmpress
hmmscan=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/hmmer-3.1b1-linux-intel-x86_64/binaries/hmmscan
get_Trinity_gene_to_trans_map=/fslgroup/fslg_BybeeLab/software/trinityrnaseq_r20131110/util/get_Trinity_gene_to_trans_map.pl
special_map_script=/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts/get_Trinity_gene_to_trans_map_MODIFIED_FOR_SPECIAL_CASES.pl
Trinotate=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/Trinotate_r20131110/Trinotate
xlsToGff=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/xlsToGff.py
signalp=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/signalp-4.1/signalp
tmhmm=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/tmhmm-2.0c/bin/tmhmm
gffToFasta=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/gffToFasta.py

# Useful files

uniprot_sprot=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/uniprot_sprot.fasta
pfam_file=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/Pfam-A.hmm
blank_sqlite=/fslgroup/fslg_BybeeLab/software/trinotate_dependencies/Blank.sqlite

# If this script runs multiple times, it needs its own directory for its own stuff.
# The tmp directory is named from the second input parameter
name=${2##*/}_tmp
if [ ! -d $name ]
then
	mkdir $name
fi
if [ ! -e $name/Trinity.fasta ]
then
	cp $1 $name/Trinity.fasta
fi
cd $name

# Pridict peptides
# Annotate transcriptomes

echo 'STEP 1 : run Trinity'
			# ASSUMED COMPLETED ALREADY

# Step 1.1 : run trinity to obtain fasta files
#$Trinity --seqType fq --JM 10G --single $1 -output trinity_output

fasta_file=Trinity.fasta

# Step 1.2 : run TransDecoder on fasta files to obtain peptide sequences ([file_name].pep)
if [ ! -e Trinity.fasta.transdecoder.pep ]
then
	$TransDecoder -t $fasta_file
fi

echo 'STEP 2 : run Blast'

# Step 2.1 : prepare SwissProt database for blast
#    download the uniprot database from http://sourceforge.net/projects/trinotate/files/TRINOTATE_RESOURCES/uniprot_sprot.fasta.gz/download
#    prep database using makeblastdb
# $makeblastdb -in uniprot_sprot.fasta -dbtype prot

# NOTE: the pipeline does not change the uniprot_sprot.fasta file, so we may reuse the same file each time.
# I already made that database, so we can just use the one I have.
# See $uniprot_sprot


# Step 2.2 : run Blastx on fasta files to find sequence homologies
if [ ! -e blastx_Trinity.outfmt6 ]
then
	$blastx -query $fasta_file -db $uniprot_sprot -num_threads 16 -max_target_seqs 1 -outfmt 6 > blastx_Trinity.outfmt6
fi

# Step 2.3 : run Blastp on pep files to find peptide homologies
if [ ! -e blastp_Trinity.outfmt6 ]
then
	$blastp -query Trinity.fasta.transdecoder.pep -db $uniprot_sprot -num_threads 16 -max_target_seqs 1 -outfmt 6 > blastp_Trinity.outfmt6
fi

echo 'STEP 3 : run HMMER for protein domain identification'

echo 'Step 3.1 : download and prepare Pfam-A.hmm'
# Download the file from http://sourceforge.net/projects/trinotate/files/TRINOTATE_RESOURCES/Pfam-A.hmm.gz/download
# prepare for use with hmmscan
# $hmmpress Pfam-A.hmm
echo 'NOTE: the pipeline does not change the Pfam-A.hmm file, so we may reuse the same file each time.'
echo 'I already prepared that file, so just use use the one I have.'
echo 'See $pfam_file'

echo 'Step 3.2 : run HMMER with Pfam-A.hmm and pep file'
if [ ! -e TrinityPFAM.out ]
then
	$hmmscan --cpu 16 --domtblout TrinityPFAM.out $pfam_file Trinity.fasta.transdecoder.pep > TrinityPFAM.log
fi

echo 'Step 4 : run signalP to predict signal peptides'
if [ ! -e Trinity_signalp.out ]
then
	$signalp -t euk -f long -n Trinity_signalp.out Trinity.fasta.transdecoder.pep
fi

echo 'Step 5 : run tmHMM to predict transmembrane regions'
if [ ! -e TrinityTMHMM.out ]
then
	$tmhmm --short < Trinity.fasta.transdecoder.pep > TrinityTMHMM.out
fi

# -------------------------------Assembling the database----------------------- #

# At this point, I had to move all my files into the same folder, otherwise Trinotate had difficulties finding the database.
# Note that each organism needs its own database. That is, this step must be done for all transcriptomes.

# THIS IS VERY IMPORTANT! The database must be named "Trinotate.sqlite" or Trinotate throws up. Do not rename the database.

# THIS IS ALSO IMPORTANT! The database cannot be in a separate folder. It must be in the same directory that you ran this script inside.

# I already downloaded a prepared database from the website, so copy my blank database into the working location, renaming it to Trinotate.sqlite

echo 'Step 6 : database production'
cp $blank_sqlite Trinotate.sqlite

# Be sure you download the correct version of the database.
# "The boilerplate Trinotate.sqlite database downloaded above is specific to each software release. The link above will retrieve the sqlite database that is compatible with this current software version (Nov 10, 2013)."

echo 'Get gene/transcript relationships map (this will be put into the database)'
$get_Trinity_gene_to_trans_map $fasta_file > Trinity.fasta.gene_trans_map
NUMOFLINES=$(wc -l < "Trinity.fasta.gene_trans_map")
if [ "$NUMOFLINES" -lt "50" ]
then
	$special_map_script $fasta_file > Trinity.fasta.gene_trans_map
fi
if [ "$NUMOFLINES" -lt "50" ]
then
    echo 'There\'s been a big error while trying to get a good gene to trans map.'
	exit
fi

echo 'Initialize the database with transcript, protein, and gene/transcrip map files'
$Trinotate Trinotate.sqlite init --gene_trans_map Trinity.fasta.gene_trans_map --transcript_fasta $fasta_file --transdecoder_pep Trinity.fasta.transdecoder.pep

echo 'Add protein hits into the database'
$Trinotate Trinotate.sqlite LOAD_blastp blastp_Trinity.outfmt6 

echo 'Add sequence hits'
$Trinotate Trinotate.sqlite LOAD_blastx blastx_Trinity.outfmt6

echo 'Add PFAM output'
$Trinotate Trinotate.sqlite LOAD_pfam TrinityPFAM.out 

echo 'Add signalp output'
$Trinotate Trinotate.sqlite LOAD_signalp Trinity_signalp.out

echo 'Add tmhmm output'
$Trinotate Trinotate.sqlite LOAD_tmhmm TrinityTMHMM.out

echo '--------------------------------Obtaining output from the database------------------------'

$Trinotate Trinotate.sqlite report > Trinity_report.xls

echo 'Convert output to gff format using a simple script'

$xlsToGff Trinity_report.xls $2

$gffToFasta $2 $fasta_file $2_extracted.fasta

echo 'Congratulations, you now have a file with annotated peptides from your transcriptome.'
