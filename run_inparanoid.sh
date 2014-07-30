#! /bin/bash

# ARGS
# $1 first file to inparanoid
# $2 second file to inparanoid

mkdir $1-$2

cd $1-$2

cp /fslhome/njensen6/software/inparanoid_to_copy/* ./

cp ../$1 ./
cp ../$2 ./

#./inparanoid_hardcoded_locations.pl $1 $2
