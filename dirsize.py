#! /usr/bin/env python

import glob
import sys

if len(sys.argv) > 0 :
	print('Length of %s : %d' %(sys.argv[1], len(glob.glob(sys.argv[1]))))

