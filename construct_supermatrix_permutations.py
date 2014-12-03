#! /usr/bin/env python

import random
random.seed()
import sys
import re
import glob

# Assume all cluster files are in the directory
# Assume all cluster files begin with the name "cluster"
# Assume the organisms in the clusters always come in the same order

def usage(program_path) :
    print ('\nUsage: %s\n' %program_path)

# Because all organisms come in order, we can pull headers from any sample file
def produce_headers(sampleFile) :
    headers = []
    file = open(sampleFile, 'r')
    for line in file :
        if line[0] == '>' :
            line = line.strip()
            line = line[1:]
            if len(line.split('|')) != 1 :
                line = line.split('|')[1]
            headers.append(">%s" %line)
    return headers

def read_files(files) :
    total = len(files)
    counter = 0
    percent = total / 10
    if percent == 0 :
        percent = 1
    headers = produce_headers(files[0])
    superArray = {}
    num_organisms = len(headers)
    print ("There are %d files." %len(files))
    print ("Progress: 0.00%")
    for filename in files :
        file = open(filename, 'r')
        contents = ""
        for line in file :
            if line[0] != '>' :
                line = line.strip()
            contents = contents + line
        file.close()
        p = re.compile(">.*\n")
        subArray = p.split(contents)
        # At this point, subArray[0] is blank
        # the first organism is in subArray[1]
        # etc.
        if (len(subArray) == 1) :
            print ("ERROR: cluster %s gave no output!" %filename)
            continue
        if (len(subArray) != num_organisms + 1) :
            print ("ERROR: cluster %s has the incorrect number of sequences (%d)." %(filename, len(subArray)))
            continue
        for i in range(1, num_organisms + 1) :
            if subArray[i] == "" :
                print ("%s has empty sequences." %file)
            if i-1 not in superArray :
                superArray[i-1] = []
            superArray[i-1].append(subArray[i])
        counter += 1
        if counter % percent == 0 :
            print ("Progress: %.2f%%" %(counter * 100.0 / total))
    return headers, superArray

def write_one(super_file, superArray, file_options, headers) :
    superMatrix = open(super_file, 'w')
    for i in range(len(superArray)) :
        superMatrix.write('%s\n' %headers[i])
        for filenum in file_options :
            superMatrix.write(superArray[i][filenum])
        superMatrix.write('\n')
    superMatrix.close()
    print ('Output is found in %s' %super_file)

def write_all(headers, superArray) :
    file_options = range(0, len(superArray[0]))
    for i in range(0, 100) :
        filename = 'super%d.fasta' %i
        random.shuffle(file_options)
        write_one(filename, superArray, file_options, headers)

# args[1] is the number of organisms
def main(args) :
    if len(args) != 1 :
        usage(args[0])
        exit()
    files = glob.glob('*aln')
    headers, supermatrix = read_files(files)
    write_all(headers, supermatrix)

if __name__ == "__main__" :
    main(sys.argv)

