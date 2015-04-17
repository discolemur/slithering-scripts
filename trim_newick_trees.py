#! /usr/bin/env python

from argparse import ArgumentParser
import shutil
import re

#####################

# The script takes one argument : file to normalize and trim (Newick format)
# It does modify the original file, so be sure to back up a copy if you need to keep it.

#####################

'''
Example pre-processed tree:
(1179_RPROL_R_EP_006_assembly_comp8711_c0_seq1_232_1443_-_1:0.304376,((1179_RPROL_OD28_Neurocordulia_yamaskanensis_A16_assembly_comp3936_c0_seq1_199_819_-_1:0.158704,(1179_RPROL_OD46_Libellula_saturnata_A18_assembly_comp3835_c0_seq1_79_1302___1:0.019462,1179_RPROL_OD45_Libellula_forensis_A12_assembly_comp2884_c0_seq1_102_1325___1:0.02392)100:0.131199)87:0.077401,((((((1179_RPROL_OD18_Chromagrion_conditum_A13_assembly_comp5783_c0_seq1_128_1348___1:0.052899,1179_RPROL_OD13_Nehalennia_gracilis_A2_assembly_comp1759_c0_seq1_193_1416_-_1:0.072091)77:0.021671,1179_RPROL_OD36_Argia_fumipennis_violacea_A14_assembly_comp7525_c0_seq1_374_1597_-_1:0.108844)34:0.014525,(1179_RPROL_OD10_Ischnura_posita_male_A5_assembly_comp2115_c0_seq1_101_1324___1:1e-06,1179_RPROL_OD43_Hetaerina_sp_A7_assembly_comp3687_c0_seq1_102_1325___1:1e-06)100:0.219953)44:0.032313,(((1179_RPROL_OD11_Ischnura_verticalis_male_A6_assembly_comp5877_c0_seq1_167_1390___1:0.012763,1179_RPROL_OD_Ischnura_cervula_sp_A19_assembly_comp9286_c0_seq1_157_1380___1:0.007582)77:0.008447,1179_RPROL_OD62_Ischnura_hastata_A19_assembly_comp12693_c0_seq1_212_1435___1:0.019637)98:0.033008,1179_RPROL_OD44_Enallagma_sp_A12_assembly_comp7660_c0_seq1_165_1388___1:0.057458)100:0.117147)99:0.142954,1179_RPROL_OD42_Archilestes_grandis_A6_assembly_comp7627_c0_seq1_199_1422_-_1:0.249909)97:0.107578,(((1179_RPROL_OD25_Stylurus_spiniceps_A15_assembly_comp2976_c0_seq1_103_1326___1:0.024241,1179_RPROL_OD12_Gomphus_spicatusA13_assembly_comp3311_c0_seq1_215_1438_-_1:0.025688)100:0.124488,(1179_RPROL_OD08_Calopteryx_maculata_A7_assembly_comp2980_c0_seq1_187_1410_-_1:0.005065,1179_RPROL_OD64_Anax_junius_A4_assembly_c5247_g1_i1_125_1348_-_1:1e-06)100:0.103221)42:0.020826,1179_RPROL_OD07_Cordulegaster_maculata_A4_assembly_comp1075_c0_seq1_218_1441_-_1:0.151903)36:0.030991)57:0.032125)100:0.336896,1179_RPROL_R_EP_001_assembly_comp6095_c0_seq1_52_1206___1:0.944037);

Example -all processed tree :
(R_EP_006,((OD28,(OD46,OD45)),((((((OD18,OD13),OD36),(OD10,OD43)),(((OD11,OD_I),OD62),OD44)),OD42),(((OD25,OD12),(OD08,OD64)),OD07))),R_EP_001);
'''

# Fix IDs
ODname = re.compile(r'([,(])[^:(,]*(OD.{2})[^:]*:')
ODname_sub = r'\1\2:'
EPname = re.compile(r'([,(])[^:(,]*(R_EP_\d{3})[^:]*:')
EPname_sub = r'\1\2:'

# Remove branch lengths (remember, some have tiny-number format 1e-06)
branch = re.compile(r':[^,)]*([,)])')
branch_sub = r'\1'

# Remove bootstrap values
boot = re.compile(r'\)\d+\.*\d*')
boot_sub = r')'

def trim_and_normalize_tree(tree, choices = None) :
    if choices is None :
        tree = ODname.sub(ODname_sub, tree)
        tree = EPname.sub(EPname_sub, tree)
        tree = branch.sub(branch_sub, tree)
        tree = boot.sub(boot_sub, tree)
    else :
        if choices['id'] :
            tree = ODname.sub(ODname_sub, tree)
            tree = EPname.sub(EPname_sub, tree)
        if choices['boot'] :
            tree = boot.sub(boot_sub, tree)
        if choices['branch'] :
            tree = branch.sub(branch_sub, tree)
    return tree

def read_trees(filename, choices = None) :
    trees = []
    fh = open(filename, 'r')
    for line in fh :
        line = line.strip()
        if len(line) != 0 :
            trees.append(trim_and_normalize_tree(line, choices))
    fh.close()
    return trees

def write_file(trees, treefile, do_overwrite) :
    newfile = '%s.trimmed' %treefile
    ofh = open(newfile,'w')
    for tree in trees :
        ofh.write('%s\n' %tree)
    ofh.close()
    if do_overwrite :
        shutil.move(newfile, treefile)

def main(treefile, choices) :
    trees = read_trees(treefile, choices)
    write_file(trees, treefile, choices['overwrite'])

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('treefile')
    parser.add_argument('-id', help='Trim ids (default is False)', action='store_true', default=False)
    parser.add_argument('-branch', help='Trim branch lengths (default is False)', action='store_true', default=False)
    parser.add_argument('-boot', help='Trim bootstrap values (default is False)', action='store_true', default=False)
    parser.add_argument('-all', help='Trim everything, leaving only tree topology (default is False)', action='store_true', default=False)
    parser.add_argument('-o', help='Overwrite existing file (default is False)', action='store_true', default=False)
    args = parser.parse_args()
    if not args.id and not args.boot and not args.branch and not args.all :
        print('Well, this is boring. You gotta tell me what to trim. Options are id, branch, boot, and all.')
        exit(0)
    choices = { 'id':args.id, 'boot':args.boot, 'branch':args.branch, 'overwrite':args.o }
    if args.all :
        choices['id'] = True
        choices['boot'] = True
        choices['branch'] = True
    main(args.treefile, choices)

