#! /usr/bin/env python

import glob
import sys

if len(sys.argv) > 1 :
	print('Length of %s : %d' %(sys.argv[1], len(glob.glob('%s/*' %sys.argv[1]))))
else :
	print(len(glob.glob('*')))
