#! /usr/bin/env python

'''

This script keeps the largest isoform and throws the rest away.

'''


from argparse import ArgumentParser

#>GENEIDpart1_GENEIDpart2_ISOFORMID|stuff
#>c7093_g1_i1|m.7449_Anax
def get_gene_id(header) :
    return '_'.join(header.split('>')[1].split('|')[0].split('_')[0:2])

# These should be collapsed.
#>c7093_g1_i1|m.7449_Anax
#>c7093_g1_i2|m.7450_Anax

class Gene(object) :
    def __init__(self, header) :
        self._header = header
        self._seq = ''
    def add_content(self, content) :
        self._seq = self._seq + content

def read_binned_fasta(infile) :
    ''' Returns a dictionary in this schema -- {GeneID(string)} -> [ Gene(object) ]
    Parameters :
        infile : string
    '''
    fasta_map = {}
    header = ''
    fh = open(infile, 'r')
    for line in fh :
        line = line.strip()
        if line[0] == '>' :
            header = line
            id = get_gene_id(header)
            if id not in fasta_map :
                fasta_map[id] = []
            fasta_map[id].append(Gene(header))
        else :
            fasta_map[id][-1].add_content(line.upper())
    fh.close()
    return fasta_map

def reduce_fasta(fasta) :
    out_genes = []
    for id in fasta :
        best = None
        for duplicate in fasta[id] :
            if best is None :
                best = duplicate
            # Keep the ones bigger than the best
            elif len(best._seq) < len(duplicate._seq) :
                best = duplicate
        out_genes.append(best)
    return out_genes

def main(infile) :
    fasta = read_binned_fasta(infile)
    out_genes = reduce_fasta(fasta)
    ofh = open('%s.trimmed.fasta' %(infile), 'w')
    for gene in out_genes :
        ofh.write('%s\n%s\n' %(gene._header, gene._seq))
    ofh.close()

if __name__ == '__main__' :
    parser = ArgumentParser()
    parser.add_argument('infile')
    args = parser.parse_args()
    main(args.infile)
