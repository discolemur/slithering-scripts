#! /usr/bin/env python

import glob
import sys

length = 0

if len(sys.argv) > 1 :
    length = len(glob.glob('%s/*' %sys.argv[1]))
else :
    length = len(glob.glob('*'))

sys.stdout.write('%d' %length)
sys.stdout.write('\n')
