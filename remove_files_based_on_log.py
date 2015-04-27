#! /usr/bin/env python
# Removes files that appear in the logfile
import os, sys
if len(sys.argv) != 2 : print('Usage: %s logfile'); exit(1)
bads = set(line.strip() for line in open(sys.argv[1],'r'))
for file in bads : os.remove(file)
