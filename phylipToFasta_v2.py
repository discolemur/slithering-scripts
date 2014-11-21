#! /usr/bin/env python

import sys

file = open(sys.argv[1], 'r')
out = open(sys.argv[2], 'w')

file.readline() # Throw away numbers

for line in file :
    line = line.strip().split(' ')
    out.write('>%s\n%s\n' %(line[0], line[1]))

out.close()
file.close()
