#! /usr/bin/env python
import shutil, sys
if len(sys.argv) != 3 : print('Usage: %s logfile target_directory'); exit(1)
goods = set(line.strip() for line in open(sys.argv[1],'r'))
for file in goods : shutil.copy(file, sys.argv[2])
