#!/usr/bin/python
# -*- coding: utf-8 -*-
import mmap
import time
from jsonmmap import ObjectMmap


def main():
    mm = ObjectMmap(-1, 1024*1024, access=mmap.ACCESS_WRITE, tagname='share_mmap')
    count = 0
    while True:
        obj = mm.jsonread_follower()
        if obj:
        	print '*' * 15 + str(count) + '*' * 15
        	print obj
        	count += 1
        else:
        	pass
        time.sleep(1)

if __name__ == '__main__':
    main()
