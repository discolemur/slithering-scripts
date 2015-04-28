#! /usr/bin/env python

import glob
import sys

# Reports the number of files that match the given pattern. Default is number of files in current directory.

if len(sys.argv) > 1 :
    print('Length of %s : %d' %(sys.argv[1], len(glob.glob(sys.argv[1]))))
else :
    print(len(glob.glob('*')))
