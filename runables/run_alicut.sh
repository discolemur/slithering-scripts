#! /bin/bash

cd orthodb_homologs
echo 's' | ALICUT_V2.3.pl
cd ..

cd orthodb_randoms
echo 's' | ALICUT_V2.3.pl
cd ..
