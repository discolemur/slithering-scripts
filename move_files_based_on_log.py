#! /usr/bin/env python
# Move files from the directory that exist in the logfile
# Yes, I was just trying to show off being able to do this in four lines. I'm very sorry that this happened.
import shutil, sys
if len(sys.argv) != 3 : print('Usage: %s logfile target_directory'); exit(1)
goods = set(line.strip() for line in open(sys.argv[1],'r'))
for file in goods : shutil.copy(file, sys.argv[2])
