#! /bin/bash

if ! [ $# == 1 ]
then
	echo 'Need one argument: file to aliscore.'
	exit 1
fi

if ! [ -e Aliscore.02.2.pl ]
then
    cp /fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore.02.2.pl ./
fi

if ! [ -e Aliscore_module.pm ]
then
    cp /fslgroup/fslg_BybeeLab/scripts/nick/aliscore/Aliscore_module.pm ./
fi

perl Aliscore.02.2.pl -i $1

