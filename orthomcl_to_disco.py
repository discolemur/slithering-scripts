#! /usr/bin/env python

from argparse import ArgumentParser

code_to_species = {
'OD07':'OD07_Cordulegaster_maculata_A4_assembly.pep.gz',
'OD42':'OD42_Archilestes_grandis_A6_assembly.pep.gz',
'OD08':'OD08_Calopteryx_maculata_A7_assembly.pep.gz',
'OD43':'OD43_Hetaerina_sp_A7_assembly.pep.gz',
'OD10':'OD10_Ischnura_posita_male_A5_assembly.pep.gz',
'OD44':'OD44_Enallagma_sp_A12_assembly.pep.gz',
'OD11':'OD11_Ischnura_verticalis_male_A6_assembly.pep.gz',
'OD45':'OD45_Libellula_forensis_A12_assembly.pep.gz',
'OD12':'OD12_Gomphus_spicatusA13_assembly.pep.gz',
'OD46':'OD46_Libellula_saturnata_A18_assembly.pep.gz',
'OD13':'OD13_Nehalennia_gracilis_A2_assembly.pep.gz',
'OD62':'OD62_Ischnura_hastata_A19_assembly.pep.gz',
'OD18':'OD18_Chromagrion_conditum_A13_assembly.pep.gz',
'OD64':'OD64_Anax_junius_A4_assembly.pep.gz',
'OD25':'OD25_Stylurus_spiniceps_A15_assembly.pep.gz',
'ODIc':'OD_Ischnura_cervula_sp_A19_assembly.pep.gz',
'OD28':'OD28_Neurocordulia_yamaskanensis_A16_assembly.pep.gz',
'EP1':'R_EP_001_assembly.pep.gz',
'OD36':'OD36_Argia_fumipennis_violacea_A14_assembly.pep.gz',
'EP6':'R_EP_006_assembly.pep.gz'
}

# Output format :
# cluster       organism        gene
# 1       Ischnura_mod.pep        c2418_g1_i7
def write_to_disco(data, outfile) :
    ''' Writes output in disco format
    '''
    fh = open(outfile, 'w')
    fh.write('#cluster\torganism\tgene\n')
    for id in data :
        for record in data[id] :
            fh.write('%s\t%s\t%s\n' %(id, record[0], record[1]))
    fh.close()

# Input format :
# odo19892: ODIc|comp9829_c0_seq1:3313-3702(+) ODIc|comp9829_c0_seq3:3313-3612(+) [...arbitrary repeats of this pattern]
def parse_orthomcl(infile) :
    ''' Returns dict from id to 2D list: {clusterID} -> [ [sp, geneid] ]
    '''
    global code_to_species
    clusters = {}
    fh = open(infile, 'r')
    for line in fh :
        line = line.strip()
        # The id should be the number only
        id = line.split(': ')[0][3:]
        clusters[id] = []
        for record in line.split(' ')[1:] :
            record = record.split('|')
            record[0] = code_to_species[record[0]]
            clusters[id].append(record)
    fh.close()
    return clusters

def main(infile, outfile) :
    data = parse_orthomcl(infile)
    write_to_disco(data, outfile)

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('infile')
    args = parser.parse_args()
    outfile = '%s.disco' %args.infile.split('.')[0]
    main(args.infile, outfile)
