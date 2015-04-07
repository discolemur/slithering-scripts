#! /usr/bin/env python

import glob
import shutil
import os

def main() :
    bads = []
    batches = glob.glob('*-*.sh')
    for batch in batches :
        dir = batch[:-3]
        sqlt = glob.glob('%s/sqltable.*' %dir)
        if len(sqlt) == 0 :
            bads.append(batch)
        elif len(sqlt) > 1 :
            print('Need to check %s by hand.' %dir)
        else :
            sqlt = sqlt[0]
            print(sqlt)
            shutil.copy(sqlt, sqlt.split('/')[1])
            shutil.rmtree(dir)
            os.remove(batch)
     if len(bads) > 0 :
         fh = open('fixem.txt', 'w')
         for batch in bads : fh.write('%s\n' %batch)
         fh.close()

if __name__ == '__main__' :
    main()
