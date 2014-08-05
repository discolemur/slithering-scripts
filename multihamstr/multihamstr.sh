#! /bin/bash

array=(fa_dir*)
for (( i=0 ; i < ${#array[@]} ; i++ ))
do
	first="${array[$i]}"	
done
