#! /usr/bin/env python

import argparse

# This script is used when some inparanoid runs failed and others succeeded, and you want to know which organisms you can use to do multiparanoid.
# So, if you have organisms A, B, C, D, E, F and G and suppose the comparisons D-E failed and F-G failed, then you can run ABCDF or ABCDG or ABCFE or ABCGE
# This was used when we were working with crazy plant transcriptomes.

def read_file(infile) :
    # Input should be in this format, where each line represents a successful inparanoid run :
    #
    # sp1-sp2
    # sp1-sp3
    # sp2-sp3
    pairs = {}
    fh = open(infile, 'r')
    for line in fh :
        line = line.strip()
        if line == '' :
            continue
        line = line.split('-')
        sp1 = line[0]
        sp2 = line[1]
        if sp1 not in pairs :
            pairs[sp1] = []
        if sp2 not in pairs :
            pairs[sp2] = []
        pairs[sp1].append(sp2)
        pairs[sp2].append(sp1)
    fh.close()
    return pairs

def find_complete_graphs(pairs) :
    graphs = [[]]
    nodes = list(pairs.keys())
    pos = 0
    while pos < len(nodes) :
        node = nodes[pos]
        i = 0
        while i < len(graphs) :
            graph = graphs[i]
            if graph is None :
                graph = []
            good = True
            if len(graph) != 0 :
                for sp in graph :
                    if sp not in pairs[node] :
                        good = False
                if good :
                    next = [node]
                    next.extend(graph)
                    graphs.append(next)
            else :
                graphs.append([node])
            i += 1
        pos += 1
        best = len(max(graphs, key=len))
        threshold = best - (len(nodes) - pos)
        print('Best %d threshold %d' %(best, threshold))
        next = []
        for graph in graphs :
            if len(graph) >= threshold :
                next.append(graph)
        graphs = next
        print('%d/%d' %(pos,len(nodes)))
        print('len(graphs) = %d' %(len(graphs)))
    return graphs

def main(pairs_file) :
    pairs = read_file(pairs_file)
    graphs = find_complete_graphs(pairs)
    print('There are %d options of size %d' %(len(graphs), len(graphs[0])))
    for graph in graphs :
        print(' '.join(graph))
        print('')

if __name__=='__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('pairs_file')
    args = parser.parse_args()
    main(args.pairs_file)
