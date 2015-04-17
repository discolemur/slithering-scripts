#! /usr/bin/env python

from argparse import ArgumentParser
import glob
import random
import numpy
import re

import sys
sys.path.insert(0, '/fslgroup/fslg_BybeeLab/scripts/nick/slithering-scripts')
from trim_newick_trees import read_trees

'''
Example pre-processed tree:
(1179_RPROL_R_EP_006_assembly_comp8711_c0_seq1_232_1443_-_1:0.304376,((1179_RPROL_OD28_Neurocordulia_yamaskanensis_A16_assembly_comp3936_c0_seq1_199_819_-_1:0.158704,(1179_RPROL_OD46_Libellula_saturnata_A18_assembly_comp3835_c0_seq1_79_1302___1:0.019462,1179_RPROL_OD45_Libellula_forensis_A12_assembly_comp2884_c0_seq1_102_1325___1:0.02392)100:0.131199)87:0.077401,((((((1179_RPROL_OD18_Chromagrion_conditum_A13_assembly_comp5783_c0_seq1_128_1348___1:0.052899,1179_RPROL_OD13_Nehalennia_gracilis_A2_assembly_comp1759_c0_seq1_193_1416_-_1:0.072091)77:0.021671,1179_RPROL_OD36_Argia_fumipennis_violacea_A14_assembly_comp7525_c0_seq1_374_1597_-_1:0.108844)34:0.014525,(1179_RPROL_OD10_Ischnura_posita_male_A5_assembly_comp2115_c0_seq1_101_1324___1:1e-06,1179_RPROL_OD43_Hetaerina_sp_A7_assembly_comp3687_c0_seq1_102_1325___1:1e-06)100:0.219953)44:0.032313,(((1179_RPROL_OD11_Ischnura_verticalis_male_A6_assembly_comp5877_c0_seq1_167_1390___1:0.012763,1179_RPROL_OD_Ischnura_cervula_sp_A19_assembly_comp9286_c0_seq1_157_1380___1:0.007582)77:0.008447,1179_RPROL_OD62_Ischnura_hastata_A19_assembly_comp12693_c0_seq1_212_1435___1:0.019637)98:0.033008,1179_RPROL_OD44_Enallagma_sp_A12_assembly_comp7660_c0_seq1_165_1388___1:0.057458)100:0.117147)99:0.142954,1179_RPROL_OD42_Archilestes_grandis_A6_assembly_comp7627_c0_seq1_199_1422_-_1:0.249909)97:0.107578,(((1179_RPROL_OD25_Stylurus_spiniceps_A15_assembly_comp2976_c0_seq1_103_1326___1:0.024241,1179_RPROL_OD12_Gomphus_spicatusA13_assembly_comp3311_c0_seq1_215_1438_-_1:0.025688)100:0.124488,(1179_RPROL_OD08_Calopteryx_maculata_A7_assembly_comp2980_c0_seq1_187_1410_-_1:0.005065,1179_RPROL_OD64_Anax_junius_A4_assembly_c5247_g1_i1_125_1348_-_1:1e-06)100:0.103221)42:0.020826,1179_RPROL_OD07_Cordulegaster_maculata_A4_assembly_comp1075_c0_seq1_218_1441_-_1:0.151903)36:0.030991)57:0.032125)100:0.336896,1179_RPROL_R_EP_001_assembly_comp6095_c0_seq1_52_1206___1:0.944037);

" Remove cluster IDs
%s/[(,]\zs[^(,]*\ze[OR]//g
" Simplify names and remove gene IDs
%s/OD.\{2\}\zs[^:]*\ze//g
%s/R_EP_0.\{2\}\zs[^:]*\ze//g
" Remove branch lengths completely.
%s/\:[0-9]*\.[0-9]*//g

Example processed tree :
(R_EP_006,((OD28,(OD46,OD45)),((((((OD18,OD13),OD36),(OD10,OD43)),(((OD11,OD_I),OD62),OD44)),OD42),(((OD25,OD12),(OD08,OD64)),OD07))),R_EP_001);
'''

def write_file(trees, ssize, counter) :
    outfile = '%d_random_iter%d.boottrees' %(ssize, counter)
    result = []
    if len(trees) > ssize :
        result = random.sample(trees, ssize)
    else :
        result = numpy.random.choice(trees, size=ssize, replace=True)

    fh = open(outfile, 'w')
    for res in result :
        fh.write('%s\n' %res)
    fh.close()

def main(ssize, iterations) :
    trees = []
    for filename in glob.glob('*.boottrees') :
        trees.extend(read_trees(filename))

    print('Found %d trees!' %len(trees))
    for i in range(1, iterations+1) :
        write_file(trees, ssize, i)
        if i % 20 == 0 :
            print('%f%%' %((i*100.0)/200.0))

if __name__ == '__main__' :
    random.seed()
    numpy.random.seed()
    parser = ArgumentParser()
    parser.add_argument('s', help='sample size', type=int)
    parser.add_argument('n', help='number of times to sample (number of files to produce.)', type=int, default=1)
    args = parser.parse_args()
    main(args.s, args.n)
