#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import random
import mmap
from jsonmmap import ObjectMmap


def main():
    mm = ObjectMmap(-1, 1024*1024, access=mmap.ACCESS_WRITE, tagname='share_mmap')
    count = 0
    while True:
        length = random.randint(1, 10)
        p = range(length)
        mm.jsonwrite(p)
        print '*' * 15 + str(count) + '*' * 15
        print mm.jsonread_follower()
        count += 1
        time.sleep(random.randint(1, 10))

if __name__ == '__main__':
    main()
