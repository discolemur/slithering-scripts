#!/usr/bin/env perl

use strict;
use warnings;


while (<>) {
    if (/>(\S+)/) {
        my $acc = $1;
        # MODIFIED FROM trinityrnaseq_r20131110 : get_Trinity_gene_to_trans_map.pl
        if ($acc =~ /^(.*c\d+_g\d+)(_i\d+)/) {
            my $gene = $1;
            my $trans = $1 . $2;

            print "$gene\t$trans\n";
        }
        else {
            print STDERR "WARNING: cannot decipher accession $acc\n";
        }
    }
}

exit(0);

