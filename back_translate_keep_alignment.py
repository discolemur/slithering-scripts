#! /usr/bin/env python

import glob
import argparse

######
# Produces back translations of peptide alignments retaining alignment structure.
# Must know locations of the .cds.fasta files
######

# This must be changed if you work with your own transcriptomes.
# This is the location of transdecoder's .cds.fasta files (backtranslations of transcribed proteomes).
cds_files_loc = '/fslgroup/fslg_BybeeLab/compute/all_illumina_trinity_transcriptomes/fasta_extracted/*.fasta'

'''
Can you align all UNTRIMMED AA 1:1 OrthoMCL clusters
-> back translate them to DNA sequences retaining the alignment structure
-> trim all the IDs to ODs /EPs
-> concatenate all the DNA alignments into one supermatrix keeping all individual ones?
'''

ingroup_only = False
paralog = False

# >c10003_g1_i1|m.13125 c10003_g1_i1|g.13125  ORF c10003_g1_i1|g.13125 c10003_g1_i1|m.13125 type:internal len:211 (+) c10003_g1_i1:3-632(+)
def read_fasta(infile, is_transdecoder = False) :
    # Read a fasta, either from the .pep file or from the .cds.fasta file
    ''' Returns a dictionary in this schema -- {header(string)} -> sequence(string)
    Parameters :
        infile : string
    '''
    fasta_map = {}
    header = ''
    fh = open(infile, 'r')
    for line in fh :
        line = line.strip()
        if line[0] == '>' :
            header = line
            if is_transdecoder :
                header = header.strip().split(' ')[-1].replace('(','_').replace(')','_').replace(':','_')
            if header not in fasta_map :
                fasta_map[header] = ''
        else :
            fasta_map[header] += line.upper()
    fh.close()
    return fasta_map


# >c10003_g1_i1|m.13125 c10003_g1_i1|g.13125  ORF c10003_g1_i1|g.13125 c10003_g1_i1|m.13125 type:internal len:211 (+) c10003_g1_i1:3-632(+)
# >100_OD08_Calopteryx_maculata_A7_assembly_comp579_c0_seq1_178-837_+_
def mimic_seq(cluster, header, transcriptome) :
    # For one sequence:
    # Mimics the alignment structure in dna using pep alignment as a template
    pep_seq = cluster[header]
    header = header.split('assembly_')[-1]
    dna_seq = transcriptome[header]
    new_seq = []
    pos = 0
    for aa in pep_seq :
        if aa == '-' :
            new_seq.append('---')
        else :
            new_seq.append(dna_seq[pos:pos+3])
            pos += 3
    return ''.join(new_seq)

# >100_OD07_Cordulegaster_maculata_A4_assembly_comp6430_c0_seq1_114-773_+_
# >100_OD_Ischnura
# >100_R_EP_001_assembly
# >OD07
def mimic_cluster(infile, dna) :
    # For an entire cluster:
    # Mimics the alignment structure in dna using pep alignment as a template
    global ingroup_only
    global paralog
    cluster = read_fasta(infile)
    new_file = 'back_translated_alignments/%s' %infile.split('/')[-1]
    ofh = open(new_file, 'w')
    for header in cluster :
        name = '%s_assembly' %'_'.join(header.split('_')[1:]).split('_assembly')[0]
        new_header = header.split('_')
        if new_header[1] == 'OD' :
            new_header = '_'.join(new_header[1:3])
        elif new_header[1] == 'R' :
            if ingroup_only :
                continue
            new_header = '_'.join(new_header[2:4])
        else :
            new_header = new_header[1]
        new_seq = mimic_seq(cluster, header, dna[name])
        if paralog :
            new_header = header[1:]
        ofh.write('>%s\n%s\n' %(new_header, new_seq))
    ofh.close()

def main() :
    global cds_files_loc
    dna_files = glob.glob(cds_files_loc)
    if len(dna_files) == 0 :
        print('None found.')
    dna = {}
    for f in dna_files :
        # name will be like OD25_Stylurus_spiniceps_A15_assembly
        name = f.split('/')[-1].split('.')[0]
        print(name)
        dna[name] = read_fasta(f, True)
    clusters = glob.glob('*.aln')
    for cluster in clusters :
        mimic_cluster(cluster, dna)

if __name__=='__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help='Ingroup only', action='store_true', default=False)
    parser.add_argument('-p', help='Contains paralogs', action='store_true', default=False)
    args = parser.parse_args()
    # This just makes the header remain unchanged
    paralog = args.p
    # This ignores all R* (ex: R_EP_002) taxa (they were the outgroup in our research)
    ingroup_only = args.i
    main()

