#! /usr/bin/env python

import glob
import argparse

# Assume all cluster files are in the directory
# Assume all cluster files begin with the name "cluster"
# Assume the organisms in the clusters always come in the same order


#                          FOR HAMSTR
# Example headers
# >2055_RPROL_OD_Ischnura_cervula_sp_A19_assembly_comp11416_c0_seq1_248_796_+_1
# >2055_RPROL_OD44_Enallagma_sp_A12_assembly_comp1721_c0_seq1_173_721_+_1
# >2055_RPROL_R_EP_001_assembly_comp6136_c0_seq1_157_708_-_1
#def get_taxa(line) :
#    return line.split('RPROL_')[1].split('_assembly')[0]


#                          FOR HAMSTR2
# Example header
# >1466.OD25_Stylurus_spiniceps_A15_assembly.comp23067_c0_seq1_33_788_+.1
#def get_taxa(line) :
#    return line.split('.')[1].split('_assembly')[0]

#                          FOR ORTHOMCL AND INPARANOID
# Example headers
# >9_OD28_Neurocordulia_yamaskanensis_A16_assembly_comp6374_c0_seq1_175-840_+_
# >27_OD11_Ischnura_verticalis_male_A6_assembly_comp5828_c0_seq1_126-974_-_
def get_taxa(line) :
    return '_'.join(line.split('_assembly')[0].split('_')[1:])

def read_file(filename, all_names, clusters) :
    fasta_map = {}
    header = ''
    fh = open(filename, 'r')
    for line in fh :
        line = line.strip()
        if line[0] == '>' :
            sp = get_taxa(line)
            all_names.add(sp)
            if sp in fasta_map :
                print('ERROR! File %s has a paralog.' %filename)
            fasta_map[sp] = ''
        else :
            fasta_map[sp] += line
    fh.close()
    clusters.append(fasta_map)
    return clusters, all_names

def compile_clusters(clusters, all_names) :
    '''
    Compile cluster maps into one final map
    Filler is important for gene losses
    '''
    final_map = {}
    for name in all_names :
        final_map[name] = ''
    for fasta_map in clusters :
        length = len(list(fasta_map.values())[0])
        filler = ''.join(['-' for i in range(length)])
        for name in all_names :
            if name in fasta_map :
                final_map[name] += fasta_map[name]
            else :
        #        print('Using filler.')
                final_map[name] += filler
    return final_map

def write_super(final_map, super_file) :
    '''
    Simply write the fasta.
    final_map is dict {name} -> sequence
    '''
    fh = open(super_file, 'w')
    for name in final_map :
        fh.write('>%s\n%s\n' %(name, final_map[name]))
    fh.close()

def build_super_matrix(files) :
    all_names = set()
    clusters = []
    total = len(files)
    counter = 0
    percent = int(total / 10)
    if percent == 0 :
        percent = 1
    print ("There are %d files." %len(files))
    print ("Progress: 0.00%")
    for filename in files :
        clusters, all_names = read_file(filename, all_names, clusters)
        counter += 1
        if counter % percent == 0 :
            print ("Progress: %.2f%%" %(counter * 100.0 / total))
    final_map = compile_clusters(clusters, all_names)
    super_file = 'super.fasta'
    print ('Writing output to %s' %super_file)
    write_super(final_map, super_file)
    print ('Output is found in %s' %super_file)

# args[1] is the number of organisms
def main(extension) :
    files = glob.glob("*%s" %extension)
    build_super_matrix(files)

if __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument('extension', help='Extension for cluster files. Common file extensions include fasta, fas, fa, pep, aln, and aa.')
    args = parser.parse_args()
    main(args.extension)

