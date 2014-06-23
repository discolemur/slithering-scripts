#! /bin/env python

import sys

#################################################################################################################################################
#																		#
#  		ORIGINAL FILE FORMAT (xls):													#
#																		#
#  gene_id        transcript_id   Top_BLASTX_hit  RNAMMER prot_id prot_coords     Top_BLASTP_hit  Pfam    SignalP TmHMM   eggnog  gene_ontology	#
#																		#
# 		 NEW FILE FORMAT (gff):														#
#																		#
#  contig_id	source	feature	start	end	score	strand	frame	attribute								#
#																		#
#################################################################################################################################################



# parses a position string into an array
# example: 323-670[-]
# becomes ['323', '670', '-']
def parsePosition(position) :
	tmp = ''
	interval = ''
	start = ''
	end = ''
	sign = ''
	for char in position :
		if char == '[' :
			interval = tmp
			tmp = ''
		elif char == ']' :
			sign = tmp
			tmp = ''
			break
		else :
			tmp = tmp + char
	for char in interval :
		if char == '-' :
			start = tmp
			tmp = ''
		else :
			tmp = tmp + char
	end = tmp
	return [start, end, sign]

# this is where we throw all the annotation information
def getAnnotation(split_line) :
	# blastx
	annotation = split_line[3] + " "
	# rnammer
	annotation = annotation + split_line[4] + " "
	# blastp
	annotation = annotation + split_line[6] + " "
	# pfam
	annotation = annotation + split_line[7] + " "
	# signalp
	annotation = annotation + split_line[8] + " "
	# tmhmm
	annotation = annotation + split_line[9] + " "
	# eggnog
	annotation = annotation + split_line[10] + " "
	# gene_ontology
	annotation = annotation + split_line[11]
	return annotation

# convert the old line into a new format
def formatLine(split_line) :
	position = parsePosition(split_line[5])
	if len(position) != 3 :
		print 'Position data does not exist when blastp does.'
		print 'This is probably a big error'
		print split_line[5]
		print position
	new_line = ''
	# contig_id
	new_line = new_line + '%s' %split_line[0]
	new_line = new_line + '\t'
	# source
	new_line = new_line + 'Trinotate'
	new_line = new_line + '\t'
	# feature
	new_line = new_line + 'Exon'
	new_line = new_line + '\t'
	# start
	new_line = new_line + '%s' %position[0]
	new_line = new_line + '\t'
	# end
	new_line = new_line + '%s' %position[1]
	new_line = new_line + '\t'
	# score
	new_line = new_line + '.'
	new_line = new_line + '\t'
	# strand
	new_line = new_line + '%s' %position[2]
	new_line = new_line + '\t'
	# frame
	new_line = new_line + '.'
	new_line = new_line + '\t'
	# attribute
	new_line = new_line + '%s %s' %(split_line[1], getAnnotation(split_line))
	new_line = new_line + '\n'
	return new_line

# write the new file's header
def writeHeader(outfile) :
	outfile.write('# The content of \'attribute\' is the transcript ID, one space, then the annotated function of the peptide\n')
	outfile.write('#contig_id\tsource\tfeature\tstart\tend\tscore\tstrand\tframe\tattribute\n')

# converts the xls format to gff format
def convertFile(infile, outfile) :
	writeHeader(outfile)
	for line in infile :
		if line[0] != '#' :
			line = line.strip()
			line = line.split('\t')
			# If the seventh column (blastp hit) is not blank
			# then the line is good, and should be processed
			# this ensures that we got exons (it matches proteins in the blast database)
			if line[6] != '.' :
				outfile.write(formatLine(line))

def usage(program_path) :
	print '\nUsage: %s <inputfile.xls> <outputfile.gff>\n' %program_path


def main(args) :
	if len(args) != 3 :
		usage(args[0])
	infile = open(args[1], 'r')
	outfile = open(args[2], 'w')
	convertFile(infile, outfile)
	infile.close()
	outfile.close()

if __name__ == "__main__" :
	main(sys.argv)
