# -*- coding:utf8 -*-

'''
Created on Aug 24,2015
Bloon Filter system


@Author : Stone <stone@bzline.cn>
'''

import sys
import os
import string
import cPickle

class BitMap(object):
    '''
    实现一个bit map,由一个整型数组组成.
    每一个int 是32位,除去最高位是符号位不使用外,还能利用32位
    所以,如果需要bitmap容纳的bit为max,那么需要这个int 数组的元素
    为 intElemt= (max+31-1)/31 (向上取整)

    注意:python 中的整数是一个对象,所以不是真正的32位的一个内存排列
         python 中的整数是一个c 语言结构(struct) 
        struct{ 
            hdr...
            int val
        }

        这个结构体中的val才是真正的int.但是我们可以不关心的理由是
        python这些运算操作也进行了同步封装,比如 i >> 2 实际转化为
        val >> 2
        具体,可以看python实现源码
    '''
    
    def __init__(self,bitmap_file):

        if os.path.exists(bitmap_file):
            data =cPickle.load(open(bitmap_file,'rb'))
            self.size =data['size']
            self.array=data['array']
        else:
            self.size = self.getElemSize(65535)
            self.array=[0 for i in range(self.size)]
   
    #获得数组的元素个数 
    def getElemSize(self,max):
        return (max+31-1)/31

    #对指定的数,获得在某一个元素上的索引
    def getElemIndex(self,num):
        return num/31

    #对指定的数,获得在某一个元素的某一个bit上的索引
    def getBitIndex(self,num):
        return num%31

    #设置指定位置上的值为1
    def setBitMask(self,num):
        elemIndex =self.getElemIndex(num)
        bitIndex =self.getBitIndex(num)
        elemValue =self.array[elemIndex]

        self.array[elemIndex]=elemValue|(1 << bitIndex)

        return

    #指定bit位置上清零
    def clearBitMask(self,num):
        elemIndex =self.getElemIndex(num)
        bitIndex =self.getBitIndex(num)
        elemValue =self.array[elemIndex]

        self.array[elemIndex]=elemValue &(~(1 << bitIndex))

        return 
        

    #测试某一个bit上的值
    #return True 表示该位置为1,存在
    def testBitMask(self,num):
        elemIndex =self.getElemIndex(num)
        bitIndex =self.getBitIndex(num)
        elemValue =self.array[elemIndex]

        if elemValue & (1 << bitIndex) : # > 0 value =1
            return True
        else: 
            return False

    def save2file(self,filename):
        data={'size':self.size,'array':self.array}
        cPickle.dump(data,open(filename,'wb'))
        return
        



class BloonHash(object):
    
    def __init__(self,max_num=65535):
        self.funcList =[]
        self.value=[]
        self.maxElemSize=max_num

        self.funcList.append(self.hash_1)
        self.funcList.append(self.hash_2)
        self.funcList.append(self.hash_3)
        self.funcList.append(self.hash_4)
        self.funcList.append(self.hash_5)
        self.funcList.append(self.hash_6)

    
    def hash_1(self,s):
        self.value.append(int(hash(s)%self.maxElemSize))

    def hash_2(self,s):
        a = 63689;  
        b = 378551;  
        v = 0;  

        for c in s:
            v = v*a + ord(c) 
            a =a*b

        self.value.append(int(v%self.maxElemSize)) 


    def hash_3(self,s):

        v = int(1315423911) 

        for c in s:
            v ^= (v << 5) + ord(c) + (v >> 2)  

        return int(v%self.maxElemSize) 

    def hash_4(self,s):
        v =0
        x =0
    
        for c in s:
            v = (v<<4) +ord(c)
            x =v&0xF0000000L
            if x!=0:
                v ^=(x>>24)
            v &=~x

        return int(v%self.maxElemSize)


    def hash_5(self,s):
        v =0 

        c=s[0]

        v=ord(c) <<7
        for c in s:
            v =(1000003*v)^(ord(c)) 
        v ^=len(s)
       
        return int(v%self.maxElemSize) 

    def hash_6(self,s):
        v =0
        
        for c in s:
            v = v<<7^ord(c)

        return int(v%self.maxElemSize)

    def set_bit_map(self,bitmap,input_string):

        self.value=[]
        for func in self.funcList:
            func(input_string)
        for hash_v in self.value: 
            bitmap.setBitMask(hash_v)



    #return False表示不存在     
    def test_bitmap(self,bitmap,input_string):
        self.value=[]
        for func in self.funcList:
            func(input_string)
           
        #只要有一个bit位不为1,则说明不存在该string 
        for hash_v in self.value:
            if bitmap.testBitMask(hash_v) ==False: #have't exists
                return False

        return True


'''
处理爬虫的url唯一性;
检查该url是否已经处理过,如果没有处理,则:
返回True,同时保持在bitmap
'''
def urlHashProcess(url,bitmap_file):

    bitmap= BitMap(bitmap_file)
    bloonhash=BloonHash()

    if bloonhash.test_bitmap(bitmap,url):# return ture,means bitmap exists this
        #only return false,do nothing
        return False
    else:
        bloonhash.set_bit_map(bitmap,url)
        bitmap.save2file(bitmap_file)
        return True


if __name__ == '__main__':
    
    #bitmap= BitMap(65535,'./bitmap')
    #bloonhash=BloonHash()

    #bloonhash.set_bit_map(bitmap,'fuckstone')

    #print bloonhash.test_bitmap(bitmap,'fuck stone')
    
    #print bloonhash.test_bitmap(bitmap,'fuck stone')
    
    #print bloonhash.test_bitmap(bitmap,'fuckstone')

    #bitmap.setBitMask(55432)
    #print bitmap.testBitMask(55430) 
    #print bitmap.testBitMask(55432)
    #print bitmap.size
    #print hash('stone')%65535

    #bitmap.save2file('./bitmap')

    print urlHashProcess('www.lexmao.com','./bitmap') 
    print urlHashProcess('www.bzline.cn','./bitmap')



