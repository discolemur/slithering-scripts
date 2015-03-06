#! /usr/bin/env python

import glob
import re

def get_taxon_name(gff_file) :
    gff_file = gff_file.split('/')[-1]
    return gff_file[:-4]

# Length is 9
# Example gff file entry
# comp10002_c0	Trinotate	Exon	3	1220	.	+	.	comp10002_c0_seq1 . cds.comp10002_c0_seq1|m.12725 sp|Q5ZI08|SPT5H_CHICK^Q5ZI08^Q:7-390,H:694-1076^53.37%ID^E:3e-118^RecName: Full=Transcription elongation factor SPT5;^Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi; Archosauria; Dinosauria; Saurischia; Theropoda; Coelurosauria; Aves; Neognathae; Galliformes; Phasianidae; Phasianinae; Gallus PF00467.24^KOW^KOW motif^12-42^E:1.2e-05`PF12815.2^CTD^Spt5 C-terminal nonapeptide repeat binding Spt4^82-198^E:2.5e-13 . . COG0250^Transcription antiterminator GO:0032044^cellular_component^DSIF complex`GO:0032968^biological_process^positive regulation of transcription elongation from RNA polymerase II promoter`GO:0006351^biological_process^transcription, DNA-dependent
def get_combo_name_gff(taxon, header) :
    '''
    Returns a combination taxonID+geneID
    '''
    header = header.split('\t')
    geneID = header[8].split(' ')[0] + '_' + header[3] + '_' + header[4] + '_' + header[6].replace('-','_') + '_'
    return taxon + '_' + geneID

go_re = re.compile(r'GO:\d{7}')
def get_third_level_GO_term(line) :
    #Get the third.
    found = go_re.findall(line)
    result = 'NA'
    if len(found) > 2 :
        result = found[2]
    return result

def get_go_terms(file, go_dict) :
    '''
    Returns: dictionary {combo_name(unique ID)} -> 3rd_level_go_term
    '''
    taxon = get_taxon_name(file)
    fh = open(file, 'r')
    for line in fh :
        line = line.strip()
        if line[0] == '#' :
            continue
        combo_name = get_combo_name_gff(taxon, line)
        # < FOR TESTING 
        go_dict[combo_name] = get_third_level_GO_term(line)
        # FOR TESTING >
    fh.close()
    return go_dict

'''
Output goal:

Hamster_pseudo_1to1

Clusters       SP1        SP2     ...

Cluster1   GO:XXXXXXX     ...
Cluster2	  GO:XXXXXXX     ...
     ...
...
  
sp - species IDs (EPs, ODs)
GO:XXXXXXX term of the 3d level 
if there is no 3d level GO term or any GO term annotated for a species in a cluster put NA or just space.
'''
# Example headers:
# HAMSTR
#>11_OD64_Anax_junius_A4_assembly_c4388_g1_i1_238_1296_+_1
# INPARANOID
#>12_OD08_Calopteryx_maculata_A7_assembly_comp7921_c0_seq1_3-467_+_
def get_combo_name_cluster(taxon, header) :
    '''
    Returns a combination taxonID+geneID
    '''
    result = taxon + '_' + header.split('assembly_')[1].replace('-', '_')
    if result[-1] == '1' :
        result = result[:-1]
    return result

def write_GOs(ofh, clusterfile, taxa, go_dict) :
    ifh = open(clusterfile, 'r')
    sp_to_combo = {}
    for line in ifh :
        if line[0] == '>' :
            line = line.strip()
            sp = line.split('assembly')[0] + 'assembly'
            sp = '_'.join(sp.split('_')[1:])
            sp_to_combo[sp] = get_combo_name_cluster(sp, line)
    ifh.close()
    for taxon in taxa :
        if taxon not in sp_to_combo :
            id = 'NA'
        else :
            id = sp_to_combo[taxon]
        if id not in go_dict :
            ofh.write('\tNA')
        else :
            ofh.write('\t%s' %go_dict[id])

def main() :
    go_dict = {}
    gff_files = glob.glob('/fslgroup/fslg_BybeeLab/compute/all_illumina_trinity_transcriptomes/inparanoid_computations/gff_files/*.gff')
    taxa = []
    for file in gff_files :
        taxa.append(get_taxon_name(file))
        go_dict = get_go_terms(file, go_dict)
    cluster_files = glob.glob('*.aln')
    ofh = open('COMPILED_GO_TERMS.txt', 'w')
    ofh.write('Clusters\t%s\n' %'\t'.join(taxa))
    for file in cluster_files :
        ofh.write(file)
        write_GOs(ofh, file, taxa, go_dict)
        ofh.write('\n')
    ofh.close()

if __name__=='__main__' :
    main()

