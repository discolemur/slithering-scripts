#! /usr/bin/env python

import sys

def main(infile) :
    mapfile = '%s_map.txt' %infile.split('.')[0]
    outfile = '%s_mod.fasta' %infile.split('.')[0]
    ifh = open(infile, 'r')
    ofh = open(outfile, 'w')
    mfh = open(mapfile, 'w')
    counter = 1
    for line in ifh :
        line = line.strip()
        if line[0] == '>' :
            ofh.write('>%d\n' %counter)
            mfh.write('%s\t%d\n' %(line[1:], counter))
            counter += 1
        else :
            ofh.write('%s\n' %line)
    mfh.close()
    ofh.close()
    ifh.close()

if __name__ == '__main__' :
    main(sys.argv[1])
