#! /usr/bin/env python

# Basic renaming script. Not super profound. Can be modified to suit many needs.

import os
import glob

print('Working...')

files = glob.glob('*gff_extracted.fasta')
for file in files :
    newname = '%s.fasta' %file.split('.')[0]
    os.rename(file, newname)

print('Done.')
