#! /usr/bin/env python

import sys
import re

def parse_and_write(infilename, outfilename) :
    infile = open(infilename, 'r')
    outfile = open(outfilename, 'w')
    outfile.write('sp1\tsp2\tdN/dS\tdN\tdS\n')
    organisms = []
    for line in infile :
        line = line.strip()
        if line == '' :
            continue
        line = re.split('[\(\)]?\s*[\(\)]?', line)
        organisms.append(line[0])
        for i in range(1, len(line)) :
            if (line[i] == '') :
                continue
            if (i % 3 == 1) :
                # sp1
                outfile.write(line[0])
                outfile.write('\t')
                org = i / 3
                # sp2
                outfile.write(organisms[org])
                outfile.write('\t')
                # dN/dS
                outfile.write(line[i])
                outfile.write('\t')
            if (i % 3 == 2) :
                # dN
                outfile.write(line[i])
                outfile.write('\t')
            if (i % 3 == 0) :
                # dS
                outfile.write(line[i])
                outfile.write('\n')
    outfile.close()
    infile.close()

def main(args) :
    if (len(args) != 3) :
        print("Usage: %s <input_matrix> <output_filename>" %args[0])
        exit()
    parse_and_write(args[1], args[2])


if __name__ == '__main__' :
    main(sys.argv)
