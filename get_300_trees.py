#! /usr/bin/env python

import glob
import random
import sys

outfile = '300_random.trees'
print('The first argument given is the output file.')
print('Default is %s' %outfile)

def read_trees(filename, trees) :
    fh = open(filename, 'r')
    for line in fh :
        trees.append(line.strip())
    fh.close()
    return trees

trees = []
for filename in glob.glob('*.boottrees') :
    trees = read_trees(filename, trees)

print('Found %d trees!' %len(trees))

result = random.sample(trees, 300)

if len(sys.argv) > 1 :
    outfile = sys.argv[1]
fh = open(outfile, 'w')
for res in result :
    fh.write('%s\n' %res)
fh.close()
