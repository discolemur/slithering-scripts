#! /usr/bin/env python

import glob
import shutil
import os

def main() :
    fh = open('fixem.txt', 'w')
    batches = glob.glob('*-*.sh')
    for batch in batches :
        dir = batch[:-3]
        sqlt = glob.glob('%s/sqltable.*' %dir)
        if len(sqlt) == 0 :
            fh.write('%s\n' %batch)
        elif len(sqlt) > 1 :
            print('Need to check %s by hand.' %dir)
        else :
            sqlt = sqlt[0]
            print(sqlt)
            shutil.copy(sqlt, sqlt.split('/')[1])
            os.rmdir(dir)
            os.remove(batch)

if __name__ == '__main__' :
    main()
