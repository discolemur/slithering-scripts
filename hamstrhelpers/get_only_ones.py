#! /usr/bin/env python

import glob

'''
>1532_R_EP_006_assembly_comp10734_c0_seq3_1_2151_-_1
. . .
>1532_R_EP_006_assembly_comp22961_c0_seq1_1_408_+_0
'''

def handle_file(file) :
    outfile = 'only_1s/%s' %file
    ifh = open(file, 'r')
    ofh = open(outfile, 'w')
    getting = False
    for line in ifh :
        if line[0] == '>' :
            if line[-2] == '1' :
                getting = True
            else :
                getting = False
        if getting :
            ofh.write(line)
    ofh.close()
    ifh.close()

files = glob.glob('*.fa')
for file in files :
    handle_file(file)

