#! /usr/bin/env python

from argparse import ArgumentParser
import glob
import random
import numpy


def read_trees(filename, trees) :
    fh = open(filename, 'r')
    for line in fh :
        trees.append(line.strip())
    fh.close()
    return trees

def main(iterations) :
    outfile = '%d_random.trees' %iterations
    print('Output is found in %s' %outfile)

    trees = []
    for filename in glob.glob('*.boottrees') :
        trees = read_trees(filename, trees)

    print('Found %d trees!' %len(trees))

    result = []
    if len(trees) > iterations :
        result = random.sample(trees, iterations)
    else :
        result = numpy.random.choice(trees, size=iterations, replace=True)

    fh = open(outfile, 'w')
    for res in result :
        fh.write('%s\n' %res)
    fh.close()

if __name__ == '__main__' :
    random.seed()
    numpy.random.seed()
    parser = ArgumentParser()
    parser.add_argument('s', help='sample size', type=int)
    args = parser.parse_args()
    main(args.s)
