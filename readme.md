python 基于mmap模块的jsonmmap实现本地多进程内存共享
================================================
###1.概述
+ 共享内存可以说是最有用的进程间通信方式.两个不用的进程共享内存的意思是:同一块物理内存被映射到两个进程的各自的进程地址空间.一个进程可以及时看到另一个进程对共享内存的更新,反之亦然.采用共享内存通信的一个显而易见的好处效率高,因为进程可以直接读写内存,而不需要任何数据的复制.对于向管道和消息队列等通信等方式,则需要在内核和用户空间进行四次的数据复制,而共享内存则只需要两次数据复制:一次从输入文件到共享内存区,另一个从共享内存区到输出文件.实际上,进程之间在共享内存时,并不总是读写少量数据后就解除映射,有新的通信时,再重新建立共享内存区域.而是保持共享区域,知道通信完毕为止,这样,数据内容就一直保存在共享内存中,并没有写回文件.共享内存中的内容往往是在解除映射时才写回文件的.因此,采用共享内存的通信方式效率非常高.

+ mmap系统调用是的是的进程间通过映射同一个普通文件实现共享内存.普通文件被映射到进程地址空间后,进程可以向像访问普通内存一样对文件进行访问,不必再调用read,write等操作.与mmap系统调用配合使用的系统调用还有munmap,msync等.
    实际上,mmap系统调用并不是完全为了用于共享内存而设计的.它本身提供了不同于一般对普通文件的访问方式,是进程可以像读写内存一样对普通文件操作.而Posix或System V的共享内存则是纯粹用于共享内存的,当然mmap实现共享内存也是主要应用之一. 

###2. python mmap模块详解
+ 在python中，mmap.mmap()的函数实现在windows和linux上是不一样的，但实现api接口函数很相似，下面以mmap的windows实现为例说明：

+ mmap.mmap(fileno, length[, tagname[, access[, offset]]]) 
    + **fileno**：the file handle fileno， 文件描述符
    + **length**：共享内存的大小
    + **tagname**: 共享内存区域的名字，可以理解为id
    + **access**:  
        + **ACCESS_READ**: 只能读，如果执行写操作，raises a TypeError exception
        + **ACCESS_WRITE**: 可读可写
        + **ACCESS_COPY**: 可读可写，但不更新到文件中去

+ 函数列表
    + **mmap.close()** 断开映射关系
    + **mmap.find(string[, start[, end]])**：返回第一个string的索引，否则返回-1
    + **mmap.move(dest, src, count)**： 移动count大小的内容从src到dest
    + **mmap.read(num)**: 根据文件指针的位置兑取num个字节的内容，更新文件指针的位置
    + **mmap.read_byte()**：读取当前字符，更新文件指针位置
    + **mmap.readline()**：Returns a single line, starting at the current file position and up to the next newline.从当前位置到下一行位置的所有内容
    + **mmap.resize(newsize)**：Resizes the map and the underlying file，改变映射内存与文件大小
    + **mmap.rfind(string[, start[, end]])**： 返回最后一个string的索引
    + **mmap.seek(pos[, whence])**： 设置文件指针的位置
    + **mmap.size()**： 返回共享内存的大小
    + **mmap.tell()**：返回当前指针的位置
    + **mmap.write(string)**：从当前指针位置开始写入string
    + **mmap.write_byte(byte)**: Write the single-character string byte into memory at the current position of the file pointer; the file position is advanced by 1. 

###3.基于mmap和json实现内存共享
+ ObjectMmap继承自mmap，结合json实现python obj的共享
    + **jsonwrite(obj)**: 将可json序列化的obj对象写入共享内存
    + **jsonread_master()**：主进程获取内存内容
    + **jsonread_follower()**: 从进程获取内存内容
+ 自定义的**jsonmmap**模块：



        #!/usr/bin/python
        # -*- coding: utf-8 -*-
        import mmap
        import json
        
        
        class ObjectMmap(mmap.mmap):
        
            def __init__(self, fileno=-1, length=1024, access=mmap.ACCESS_WRITE, tagname='share_mmap'):
                super(ObjectMmap, self).__init__(self, fileno, length, access=access, tagname=tagname)
                self.length = length
                self.access = access
                self.tagname = tagname
        
            def jsonwrite(self, obj):
                try:
                    self.obj = obj
                    self.seek(0)
                    obj_str = json.dumps(obj)
                    obj_len = len(obj_str)
                    content = str(obj_len) + ":" + obj_str
                    self.write(content)
                    self.contentbegin = len(str(obj_len)) + 1
                    self.contentend = self.tell()
                    self.contentlength = self.contentend - self.contentbegin
                    return True
                except Exception, e:
                    return False
        
            def jsonread_master(self):
                try:
                    self.seek(self.contentbegin)
                    content = self.read(self.contentlength)
                    obj = json.loads(content)
                    self.obj = obj
                    return obj
                except Exception, e:
                    if self.obj:
                        return self.obj
                    else:
                        return None
        
            def jsonread_follower(self):
                try:
                    self.seek(0)
                    index = self.find(":")
                    if index != -1:
                        head = self.read(index + 1)
                        contentlength = int(head[:-1])
                        content = self.read(contentlength)
                        obj = json.loads(content)
                        self.obj = obj
                        return obj
                    else:
                        return None
                except Exception, e:
                    if self.obj:
                        return self.obj
                    else:
                        return None


### 4.举例
+ **主进程**：
        
        #!/usr/bin/python
        # -*- coding: utf-8 -*-
        import mmap
        from jsonmmap import ObjectMmap
        import random


        def main():
            mm = ObjectMmap(-1, 1024*1024, access=mmap.ACCESS_WRITE, tagname='share_mmap')
            while True:
                length = random.randint(1, 100)
                p = range(length)
                mm.jsonwrite(p)
                print '*' * 30
                print mm.jsonread_master()
        
        if __name__ == '__main__':
            main()

+ **从进程**：

        #!/usr/bin/python
        # -*- coding: utf-8 -*-
        import mmap
        from jsonmmap import ObjectMmap
        import time
        
        
        def main():
            mm = ObjectMmap(-1, 1024*1024, access=mmap.ACCESS_READ, tagname='share_mmap')
            while True:
                print '*' * 30
                print mm.jsonread_follower()
        
        if __name__ == '__main__':
            main()

### 5.应用场景
主进程+多个从进程，主进程负责管理多个从进程，主从进程共享一个可序列化json对象，譬如说共享配置；
主进程才具备权限去修改配置，从进程仅仅具备访问权限。

详情请参见[dragondjf github][gitaddr]

[gitaddr]: https://github.com/dragondjf/jsonmmap
