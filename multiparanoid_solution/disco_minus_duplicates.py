#! /usr/bin/env python

import argparse
from operator import itemgetter

def write_split_line(of_handle, split) :
    size = len(split)
    for i in range(0, size - 1) :
        of_handle.write('%s\t' %split[i])
    of_handle.write('%s\n' %split[size - 1])

def write_output(of_handle, lines) :
    for line in lines :
        write_split_line(of_handle, line)

#         Example header lines:
# >cds.comp10002_c0_seq1|m.12725 comp10002_c0_seq1|g.12725  ORF comp10002_c0_seq1|g.12725 comp10002_c0_seq1|m.12725 type:5prime_partial len:406 (+) comp10002_c0_seq1:3-1220(+)
# >comp10002_c0_seq1:3-1220(+)
# This function should work for both headers, and keep exactly the data shown in the second example.
def parse_header(line) :
    if len(line[1:].split(' ')) == 1 :
        return line[1:]
    return line[1:].split(' ')[-1]

# For each file,
# Search that file for ids in solution.disco
# If id is in solution.disco, add the disco line to lines
def search_files(disco) :
    lines = []
    files = list(disco.keys())
    for file in files :
        print('Searching %s' %file)
        in_handle = open(file, 'r')
        ids = set()
        for line in in_handle :
            if line[0] == '>' :
                line = line.strip()
                seq_id = parse_header(line)
                if seq_id in ids :
                    print('Duplicate id: %s' %seq_id)
                ids.add(seq_id)
                if seq_id in disco[file] :
                    lines.append(disco[file][seq_id])
        in_handle.close()
    # Sort by first column (cluster id)
    return sorted(lines, key=itemgetter(0))

def handle_input_line(of_handle, line, disco) :
    if line[0] == '#' :
        of_handle.write(line)
    else :
        line = line.strip().split('\t')
        pep = line[1]
        seq_id = line[2]
        if pep not in disco :
            disco[pep] = {}
        disco[pep][seq_id] = line
    return disco

def handle_disco(file) :
    if_handle = open(file, 'r')
    disco_out = '%s_trimmed.disco' %file.split('.')[0]
    of_handle = open(disco_out, 'w')
    disco = {}
    counter = 0
    for line in if_handle :
        disco = handle_input_line(of_handle, line, disco)
        counter += 1
    print('Read %d lines.' %counter)
    lines = search_files(disco)
    print('Will write %d lines.' %len(lines))
    write_output(of_handle, lines)
    of_handle.close()
    if_handle.close()
    return True

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Usually solution.disco or some other disco file.')
    args = parser.parse_args()
    disco_in = args.input
    handle_disco(disco_in)

if __name__ == '__main__' :
    main()
