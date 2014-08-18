#! /bin/env python

import os
import glob

print('Working...')

files = glob.glob('*.fas')
for file in files :
	newname = file[1:]
	os.rename(file, newname)

print('Done.')
