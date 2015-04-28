#! /usr/bin/env python

import glob
import sys

# Reports the size of the directory specified (default is current directory)

length = 0

if len(sys.argv) > 1 :
    pattern = sys.argv[1]
    if pattern == '*' :
        # Print size of directories.
        contents = glob.glob('*')
        length = len(contents)
        sys.stdout.write('.\t%d\n' %length)
        import os
        for name in contents :
            if os.path.isdir(name) :
                sys.stdout.write('%s\t%d\n'%(name, len(glob.glob('%s/*'%name))))
    else :
        length = len(glob.glob('%s/*' %pattern))
        sys.stdout.write('%d\n' %length)
else :
    length = len(glob.glob('*'))
    sys.stdout.write('%d\n' %length)


