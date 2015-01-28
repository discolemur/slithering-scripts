#! /usr/bin/env python

import glob

'''
This script counts the number of species and number of genes in each cluster.
The input is a .disco file.
'''

def count_disco(clusters) :
    num_genes_arr = []
    num_sp_arr = []
    ids = []
    for id in clusters :
        cluster = clusters[id]
        species = set()
        for item in cluster :
            sp = item[0]
            species.add(sp)
        num_genes = len(cluster)
        num_sp = len(species)
        num_genes_arr.append(num_genes)
        num_sp_arr.append(num_sp)
        ids.append(id)
    return num_genes_arr, num_sp_arr, ids

def read_disco(file) :
    fh = open(file, 'r')
    clusters = {}
    for line in fh :
        if line[0] == '#' :
            continue
        line = line.strip().split('\t')
        if line[0] not in clusters :
            clusters[line[0]] = []
        clusters[line[0]].append(line[1:])
    fh.close()
    return clusters

def write_result(file, num_genes_arr, num_sp_arr, ids) :
    outfile = '%s.counts' %file
    fh = open(outfile, 'w')
    fh.write('#id\tnum_genes\tnum_species\n')
    for i in range(len(ids)) :
        fh.write('%s\t%s\t%s\n' %(ids[i], num_genes_arr[i], num_sp_arr[i]))
    fh.close()

def main() :
    files = glob.glob('*.disco')
    for file in files :
        clusters = read_disco(file)
        num_genes_arr, num_sp_arr, ids = count_disco(clusters)
        write_result(file, num_genes_arr, num_sp_arr, ids)

if __name__ == '__main__' :
    print('Working.')
    main()
    print('Done.')
