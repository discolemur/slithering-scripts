#! /bin/bash

# This simple command just runs a vim script and exits vim.

# NOTE THAT THIS IS A SLOW PROCESS!
# IF YOU REALLY WANT TO DO MASSIVE BATCH WORK, USE PYTHON OR ANOTHER REAL LANGUAGE!

#$1 is vim script
#$2 is file

echo ':wq' | vim -N -u NONE -n -c "set nomore" -S $1 $2
