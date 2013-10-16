#!/usr/bin/python
# -*- coding: utf-8 -*-
import mmap
import time
from jsonmmap import ObjectMmap


def main():
    mm = ObjectMmap(-1, 1024*1024, access=mmap.ACCESS_READ, tagname='share_mmap')
    while True:
        print '*' * 30
        print mm.jsonread_follower()

if __name__ == '__main__':
    main()
