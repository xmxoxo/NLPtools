#!/usr/bin/env python3
#coding:utf-8
# update:  2019/1/16 

'''
文件批量处理工具 

版本: v0.1.4

可对目录下的文件进行以下批量处理：
* 清除空格 空行 按句子分行；
* 删除空文件，找到后改名（原文件.del) 或者直接删除
* 删除重复的文件   根据文件的MD5判断文件是否相同，找到后改名（原文件.same)或者直接删除
* 批量重命名    可按序号进行重命名，默认从1开始，文件名会自动在前面补0，例如"0001.txt"
* 可统计文本文件的行数  [2019/1/18 添加]
* 对数据进行检查；
* 对数据重复数据检查并删除；
* 对数据进行随机打乱；
* 处理参数可以自定义顺序，
例子：

可以先处理，再删除相同文件，最后从1000开始重命名
python filetools.py ./dat p s 1 r 1000

也可以先处理，再删除空文件，再找出相同文件改名，最后从28开始重命名
python filetools.py ./dat p d 1 s r 28

可对目录下的文件进行批量处理: 以下参数的顺序可以根据实际需要调整
    [p|pre]                 文本预处理，删除文件中的空格，空行，并按句子分行
    [s|same [0|1]]          查找内容相同的文件，改名(0)或者删除(1),默认为0
    [d|del  [0|1]]          查找空文件，改名(0)或者删除(1),,默认为0
    [r|ren  [N]]            从N开始批量重命名，默认起始编号为1
    [l|line ]               统计文件行数
    [m|merge outfile]       合并文件,outfile为合并后文件,未指定则自动命名为 merge+YYYYMMDDHHNNSS+随机.txt
    [c|count]               统计文件标签情况
    [check [0|1]]           检查数据文件格式化情况, 1= 删除重复数据
    [sample]                对数据进行随机抽样
    [split [Scale]]         将指定数据文件按比例拆分成三个数据集，默认为6,2,2

命令行使用说明:
usage: python filetools.py workdir [p|pre] [s|same [1]] [d|del [1]] [r|ren [N]]

'''

__author__ = 'xmxoxo'

import sys
import os
import re
import hashlib
import random
import time
import string
import pandas as pd
import numpy as np

from bert_base.client import BertClient


# 读入文件
def readtxtfile(fname):
    pass
    with open(fname,'r',encoding='utf-8') as f:  
        data=f.read()
    return data

#保存文件
def savetofile(txt,filename):
    pass
    with open(filename,'w',encoding='utf-8') as f:  
        f.write(str(txt))
    return 1

#文本内容清洗（含HTML）
def fmtText (txt):
    pass
    #删除HTML代码
    p = re.compile(r'(<(style|script).*</\2>)|(<!--.*-->)|(<[^>]+>)',re.S)
    txt = re.sub(p,r"",txt)
    #HTML实体替换
    dictKey = {
            '&quot;': '"',
            '&apos;': '\'',
            '&amp;': '&',
            '&lt;':'<',
            '&gt;':'>',
            }
    txt = replace_dict(txt,dictKey)
    #删除其它HTML实体
    txt = re.sub('(&[#\w\d]+;)',r"",txt)
    #空格，制表符换成半角空格
    txt = re.sub('([　\t]+)',r" ",txt)  
    #多个连续的空格换成一个空格
    txt = re.sub('([ "?\t]{2,})',r" ",txt)  
    #删除空行
    txt = re.sub('(\n\s+)',r"\n",txt)
    # 中文之间的空格 [\u4e00-\u9fa5]
    #txt = re.sub('(\n\s+)',r"\1\2",txt)
    return txt


def replace_dict (txt,dictKey):
    pass
    for k,v in dictKey.items() :
        txt = txt.replace(k,v)
    return txt

#客服数据提取
def kfpick (txt):
    pass
    #多聊天记录分隔拆分 
    pS = re.compile(r'#\n展开',re.S)
    lstTxt = re.split(pS, txt)
    
    #pB = re.compile(r'(.*?)(?:\[(?:工号|客服)\])',re.S)
    pB = re.compile(r'(.*?)\n\[',re.S)
    txt = re.sub(pB, r"[",txt,count=1)

    pQ = re.compile(r'(\[客户\])(.+?)(时间: \d{4}-\d{2}-\d{2} (?:\d{2}:?){3} \n)',re.S)
    pA = re.compile(r'(\[工号\])(.+?)(时间: \d{4}-\d{2}-\d{2} (?:\d{2}:?){3} \n)',re.S)
    txt = re.sub(pQ, r"C:",txt)
    txt = re.sub(pA, r"S:",txt)
    return txt


#预处理1 去空行 空格
def delspace(txt):
    pass 
    txt = re.sub('([　\t]+)',r" ",txt)  #去掉特殊字符
    txt = re.sub('([ "?\t]{2,})',r" ",txt)  #多个连续的空格换成一个空格
    txt = re.sub('(\n\s+)',r"\n",txt)  # blank line
    #全角替换 
    #txt = txt.replace('％','%')
    #txt = txt.replace('、','')    
    return txt

# 切分句子
def cut_sent1(txt):
    txt = delspace(txt)
    txt = re.sub('([;；。！？\?])([^”])',r"\1\n\2",txt) # 单字符断句符，加入中英文分号
    txt = re.sub('(\.{6})([^”])',r"\1\n\2",txt) # 英文省略号
    txt = re.sub('(\…{2})([^”])',r"\1\n\2",txt) # 中文省略号
    #txt = re.sub('(”)','”\n',txt)   # 把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    txt = txt.rstrip()       # 段尾如果有多余的\n就去掉它
    nlist = txt.split("\n") 
    nnlist = [x for x in nlist if x.strip()!='']  # 过滤掉空行
    return nnlist


# 切分句子
def cut_sent(txt):
    txt = delspace(txt)
    txt = re.sub('([。])',r"\1\n",txt) # 单字符断句符，加入中英文分号
    #txt = re.sub('(\.{6})([^”])',r"\1\n\2",txt) # 英文省略号
    #txt = re.sub('(\…{2})([^”])',r"\1\n\2",txt) # 中文省略号
    #txt = re.sub('(”)','”\n',txt)   # 把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    txt = txt.rstrip()       # 段尾如果有多余的\n就去掉它
    #txt = re.sub('(\n"|"\n)',r"\n",txt)  #行开头与行结尾的引号去掉
    #txt = re.sub('(["])',r'""',txt)    #剩下的引号换成2个
    #nlist = txt.split("\n") 
    nlist = txt.splitlines()
    nlist = [x for x in nlist if x.strip()!='']  # 过滤掉空行
    return nlist

#对专家信息文本进行分类, 
#一行为一条信息，同时处理多条信息，并返回list格式结果
def class_pred_expert (text):
    pass
    lst_Result = []
    lstTxt = text.splitlines()
    print("total Lines: %d" % ( len(lstTxt) ) )
    bc = BertClient(ip='192.168.15.111', port=5565, port_out=5566, show_server_config=False, check_version=False, check_length=False,timeout=10000 ,  mode='CLASS')
    start_t = time.perf_counter()
    for txt in lstTxt:
        #文本拆分成句子
        list_text = cut_sent(txt)
        intTotal = len(list_text)
        #print("total setance: %d" % (intTotal) )
        #with BertClient(ip='192.168.15.111', port=5565, port_out=5566, show_server_config=False, check_version=False, check_length=False,timeout=10000 ,  mode='CLASS') as bc:
        rst = bc.encode(list_text)
        #print('result:' , rst)
        #返回结构为：
        # rst: [{'pred_label': ['0', '0', '0'], 'score': [0.9983683228492737, 0.9988993406295776, 0.9997349381446838]}]

        #标注结果分类
        pred_label = rst[0]["pred_label"]
        #index_list = np.array(pred_label).argsort().tolist()
        lstLineResult = [[],[],[],[],[]]
        for x in range(intTotal):
            #print(x, int(pred_label[x]), list_text[x])
            lstLineResult[int(pred_label[x])].append (list_text[x])

        #result_txt = [pred_label[index_list[x]] + "\t" + list_text[index_list[x]] for x in range(intTotal)]

        lst_Result.append(lstLineResult)
    print('time used:{}'.format(time.perf_counter() - start_t))
    return lst_Result

# 对专家信息文本文件进行处理分类，一行为一条信息
def expert_class (fname):
    pass
    if not os.path.isfile(fname):
        print("请指定单个文件进行处理")
        return 0

    txt = readtxtfile(fname)
    lstResult = class_pred_expert(txt)
    #print(lstResult)
    #把list处理成文本，list格式有三层结构，如下：
    #[ [ 行 [分类0],[分类1],[分类2],[分类3],[分类4] ], ...]
    #lsttmp = [ '\n'.join(z) for x in lstResult for y in x for z in y]
    #print(lsttmp)
    strText = ""
    for x in lstResult:
        for y in x:
            strText += '"' +  '\n'.join(y) + '",'  #'\n' + '-'*30 + '\n'
        strText += '\n'
    #print(strText)
    #saveto file 
    savetofile(strText, fname[:fname.rfind ('.')] + '-class' + fname[fname.rfind ('.'):]) 

#客服内容提取
def pre_kf (path):
    pass
    intTotalLines = 0
    lstF = getFiles(path)

    for fname in lstF[1] :
        txt = readtxtfile(fname)
        txt = fmtText(txt)
        txt = kfpick(txt)
        nfname = fname[:fname.rfind ('.')] + '-pick.txt'
        savetofile(txt, nfname)  
        print('Processing file:%s' % (fname))
    print('Total: %d File(s)' % (len(lstF[1]) ) )


#文本内容清洗（含HTML格式去除）
def pre_format (path):
    pass
    intTotalLines = 0
    lstF = getFiles(path)

    for fname in lstF[1] :
        txt = readtxtfile(fname)
        txt = fmtText(txt)
        savetofile(txt, fname)  
        print('Processing file:%s' % (fname))
    print('Total: %d File(s)' % (len(lstF[1]) ) )

# get all files and floders in a path
# return: 
#    return a list ,include floders and files , like [['./aa'],['./aa/abc.txt']]
def getFiles (workpath):
    lstFiles = []
    lstFloders = []

    if os.path.isdir(workpath):
        for dirname in os.listdir(workpath) :
            file_path = os.path.join(workpath, dirname)
            if os.path.isfile( file_path ):
                lstFiles.append (file_path)      
            if os.path.isdir( file_path ):
                lstFloders.append (file_path)      

    elif os.path.isfile(workpath):
        lstFiles.append(workpath)
    else:
        #print("无法识别的文件或者目录！")
        return None
    
    lstRet = [lstFloders,lstFiles]
    return lstRet


#批量重命名，对目录下的所有文件按序号开始命名；
#序号会根据文件的数量自动在前面补0，例如有1000个文件，则第一个文件名为：0001.txt
#执行过程中将输出重命名信息，例如：
#   [./dat/akdjf.txt] =rename=> [./dat/0023.txt]
#参数：
#   path        目录。不会处理子目录；
#   intBegin    开始序号。默认=1，即从1开始命名。
#返回
#   无返回值

def brename (path ,intBegin = 1 ):
    #命名的开始序号,
    #intBegin = 1

    lstF = getFiles(path)
    lstRen = []
    intFNWidth = len(str(len(lstF[1])))
    for f in lstF[1] :
        #扩展名
        if f.rfind('.')>=0:
            strExt = f[f.rindex ('.'):]
        else:
            strExt = ''

        #生成新的文件名
        # 2019/1/16 按最大长度在前面补0，这样文件名排序看起来方便；例如：0023
        nfname = os.path.join(path , str(intBegin).zfill(intFNWidth)) + strExt
        print('[%s] =rename=> [%s]' %(f,nfname))
        
        intBegin += 1

        #判断是否目标与源文件同名, 例如 1.txt==>1.txt
        if f == nfname:
            continue

        #判断是否在重复列表中
        if f in lstRen :
            f = f + '.ren'
        
        #To do 判断是否会重名，也就是判断是否已经存在目标文件，存在则重命名
        if os.path.exists(nfname):
            #添加到重名列表中,然后改名
            lstRen.append(nfname)
            os.rename(nfname, nfname + '.ren' )

        os.rename(f, nfname)

        #调试用
        if intBegin>10:
            pass
            #break
        


#判断是否为空文件
#空文件是替换了空格，制表符
def blankfile (fname):
    pass
    txt = readtxtfile(fname)
    txt = delspace(txt)
    txt = txt.replace('\n','')
    txt = txt.replace('\r','')
    if txt == "":
        return fname
    else:
        return ''

#删除目录下的空文件 
def delblankfile (path, isDel = False):
    lstF = getFiles(path)
    for f in lstF[1] :
        print('\rfile:%s' % f,end = '')
        #print('file:%s' % f)
        if blankfile(f):
            print('\rblank file: %s' % f)
            if isDel:
                os.remove(f)
            else:
                os.rename(f, f+'.del')
    print('\r'+' '*60)


#计算文本的MD5值
def txtmd5 (txt):
    pass
    #m = hashlib.md5()
    strMD5 = hashlib.md5(txt.encode(encoding='UTF-8')).hexdigest()
    return strMD5


#判断内容相同的文件，使用MD5进行计算
#参数：
#    dicHash        哈希表，用来存放文件名与哈希值对应关系；
#    strFileName    文件名，用来标识文件，也可用完整路径；
#    strBody        文件内容
#返回：
#    None 则表示没有重复，并且会更新哈希表
#    重复时返回重复的文件名  
def SameFile (dicHash, strFileName, strBody):
    pass
    strMD5 = txtmd5(strBody)
    if strMD5 in dicHash.keys():
        #冲突表示重复了
        return dicHash[strMD5]
    else:
        dicHash[strMD5] = strFileName
        return None


#检查目录下文件内容是否相同,使用MD5值来判断文件的相同。
#相同的文件可以直接删除或者改名为"原文件名.same",
#同时输出提示信息,例如：
#    File [./dat/1.txt] =same=> [./dat/92.txt] 
#参数:
#   path    要检查的目录；只检查该目录不包含子目录；
#   isDel   是否要删除，默认为否。 为“是”时直接删除文件，为“否”时将文件改名
#返回：
#   无
#
def FindSameFile (path, isDel = False):
    dicHash = {}
    lstF = getFiles(path)
    for fname in lstF[1] :
        print('\rcheck file:%s' % fname,end = '')
        txt = readtxtfile(fname)
        strSame = SameFile(dicHash,fname,txt)
        if strSame:
            print('\rFile [%s] =same=> [%s] ' % (fname,strSame))
            if isDel:
                os.remove(fname)
            else:
                os.rename(fname, fname + '.same')
            #break
    print('\r'+' '*60)


#根据系统返回换行符
def sysCRLF ():
    if os.name == 'nt':
        strCRLF = '\n'
    else:
        strCRLF = '\r\n'
    return strCRLF

'''
生成随机的字符串，可用于文件名等
参数：
    strlen  字符串长度，默认为10

返回： 
    成功返回 生成的字符串
    失败返回 None
'''
def  get_randstr (strlen = 10):
    try:
        ran_str = ''.join(random.sample(string.ascii_letters + string.digits, random.randint(strlen, strlen)))
        return ran_str
    except Exception as e :
        logging.error('Error in get_randstr: '+ traceback.format_exc())
        return None


#根据时间自动生成文件名
def autoFileName (pre = '',ext = ''):
    pass
    filename = ('%s%s%s' % (pre, time.strftime('%Y%m%d%H%M%S',time.localtime()) + get_randstr(5) , ext))
    return filename

#文本预处理，删除文件中的空格，空行，并按句子分行；
def pre_process (path,addFirstLine = 0):
    i = 0 
    lstF = getFiles(path)
    for fname in lstF[1] :
        #print('\rProcessing file:%s' % fname,end = '')
        print('Processing file:%s' % fname)
        txt = readtxtfile(fname)
        #按句子拆分
        lstLine = cut_sent(txt)

        #2019/1/17 加上分类列
        #lstLine = [ '0\t'+x for x in lstLine ]
        #2019/1/22改为调用函数实现
        lstLine = pre_addcolumn(lstLine)

        # 2019/1/17 发现一个坑,linux下和windows下的"\n"竟然不一样,只好用os.name来判断，
        strCRLF = sysCRLF()
        txt = strCRLF.join(lstLine)
        
        #保存到文件
        if addFirstLine:
            txt = "label\ttxt\n" + txt
        savetofile(txt, fname )  
        i += 1
        #if i>9:
        #    pass
            #break
    #print('\r'+' '*60)
    print('Total files: %d' % i)

#NER标注处理，一个字一行
def pre_NER (txt):
    pass
    lstL = list(txt)
    strRet = sysCRLF().join(lstL)
    return strRet

#每行加上空列，参数可指定空列在行首还是行尾,默认为行首
#参数： lsttxt 每行的list
def pre_addcolumn (lsttxt,lineBegin = 1):
    pass
    if lineBegin:
        lstLine = [ '0\t'+x for x in lsttxt ]
    else:
        lstLine = [ x+'\t0' for x in lsttxt ]
    return lstLine

#判断数据文件第N列是否全为0 ，默认N=1
#2019/1/23 xmxoxo
def pre_allzero (lsttxt,lineNo = 1):
    pass
    ret = True
    for line in lsttxt:
        lstW = line.split('\t')
        if lstW[lineNo-1] != 0:
            ret = False
            break
    return ret

##使用pandas对样本数据文件进行检查；
def pd_datCheck (lstFile, drop_dup = 0):
    pass
    try:
        print("正在检查数据文件: %s \n" % lstFile)
        df = pd.read_csv(lstFile,delimiter="\t")
        print("数据基本情况:".center(30,'-'))
        print(df.index)
        print(df.columns)
        #print(df.head())
        print('正在检查重复数据：...')
        dfrep = df[df.duplicated()]
        print('重复数据行数:%d ' % len(dfrep))
        print(dfrep)
        if drop_dup and len(dfrep) :
            print('正在删除重复数据：...')
            df = df.drop_duplicates()
            df.to_csv(lstFile,index=0,sep = '\t')
        print('\n')
        print("数据分布情况:".center(30,'-'))
        dfc = df[df.columns[0]].value_counts()
        print('数值分类个数：%d' % len(dfc))
        #print('-'*30)
        print(dfc.head())
        print('\n')
        print("空值情况:".center(30,'-'))
        dfn = df[df.isnull().values==True]
        print('空值记录条数: %d ' % len(dfn))
        if not len(dfn):
            print(dfn.head())
        print('\n')
        return 0
    except Exception as e :
        print("Error in pd_dat:")
        print(e)
        return -1    

# 使用pandas 对数据集进行切割


##使用pandas 对数据进行随机样本化；
def pd_datSample (lstFile):
    pass
    try:
        print("正在随机化数据: %s" % lstFile)
        df = pd.read_csv(lstFile,delimiter="\t")
        df = df.sample(frac=1)
        #df.sample(frac=1).reset_index(drop=True)
        df.to_csv(lstFile,index=0,sep = '\t')
        return 0
    except Exception as e :
        print("Error in pd_datSample:")
        print(e)
        return -1    

##统计文本中某类标签情况
def pre_labelcount (lsttxt , columnindex = 0,labelvalue = '0'):
    pass
    intLabel = 0
    for line in lsttxt:
        lstW = line.split('\t')
        if lstW[columnindex] == str(labelvalue):
            intLabel += 1
    return intLabel

#字符串转化为整数型List,用于参数传递
#默认拆分符号为英文逗号","
def str2List (strText,sp = ',' ):
    try:
        ret = strText.split(sp)
        ret = [int(x) for x in ret]
        return ret
    except Exception as e :
        print("Error in str2List:")
        print(e)
        return None    
#Todo:
#将指定的数据文件按指定的比例拆分成三个数据集(train,dev,test)
#默认比例为 train:dev:test = 6:2:2 
#自动将文件保存到当前目录下；
#参数：
#返回：无
def splitset(datfile, lstScale =[6,2,2]):
    pass
    if len(lstScale)!=3:
        return -1
    txt = readtxtfile(datfile)
    lstLines = txt.splitlines()
    intLines = len(lstLines)-1
    #取出第一行
    strFirstLine = lstLines[0]
    #切分数据集
    lstS = [sum(lstScale[:x])/sum(lstScale) for x in range(1,len(lstScale)+1)]                        
    lstPos = [0] + [int(x*intLines) for x in lstS] #
    lstFile = ['train','dev','test']
    for i in range (len(lstFile)):
        lstDat = lstLines[lstPos[i]+1:lstPos[i+1]+1]
        if lstDat:
            fName = './%s.tsv' % lstFile[i]
            savetofile(strFirstLine + '\n' + '\n'.join(lstDat),fName)
            print('%d  Lines data save to: %s' % (len(lstDat), fName) )

#统计目录下所有文件的label分布情况
def LabelCount (path,renfile = 0):
    pass
    lstF = getFiles(path)
    intTotalLines = 0
    intLabelLines = 0

    for fname in lstF[1] :
        txt = readtxtfile(fname)
        lsttxt = txt.splitlines()
        intLines = len(lsttxt)
        intTotalLines += intLines

        #blnZero = pre_allzero(lsttxt)
        #统计第0列有多少个"1"
        intLabel = pre_labelcount (lsttxt,0,"1")
        intLabelLines += intLabel
        #如果renfile开关为1，并且 文件中没有标注，并且文件名不包含"-blank"
        #那么就改名
        if renfile and not intLabel and (not '-blank' in fname):
            os.rename(fname, fname[:-4] + '-blank' + fname[-4:] )

        print('Processing file:%20s ==> %5d lines, label count: %4d (%2.2f%%) ' % (fname,intLines,intLabel , intLabel*100/intLines ))
    print('%d File(s) ,Total: %d line(s), Laebls: %d (%2.2f%%)' % ( len(lstF[1]),intTotalLines,intLabelLines, intLabelLines*100/intTotalLines ) )

#标注数据检查 2019/2/22
def DatCheck ():
    pass
    lstF = getFiles(path)
    intTotalLines = 0

    for fname in lstF[1] :
        print("Check Dat File: %s" % fname)
        pd_datCheck(fname)
        '''
        txt = readtxtfile(fname)
        lsttxt = txt.splitlines()
        intLines = len(lsttxt)
        print("total lines:%d" %intLines)
        for line in lsttxt:
            lstW = line.split('\t')
            if len(lstW) != 2 :
                print (lsttxt.index(line))
                print (lstW)
                print('-'*30)
        '''

    #print('%d File(s) ,Total: %d line(s)' % ( len(lstF[1]),intTotalLines ) )

#随机删除0标记的行，使得01标识行数相等（未完成）
def GenNewDat ():
    pass
    lstF = getFiles(path)
    intTotalLines = 0
    for fname in lstF[1] :
        pass
    

#文本行数统计：
def linesCount (path):
    pass
    lstF = getFiles(path)
    intTotalLines = 0

    for fname in lstF[1] :
        txt = readtxtfile(fname)
        intLines = len(txt.splitlines())
        intTotalLines += intLines
        print('Processing file:%s ==> %d lines' % (fname,intLines))
    print('%d File(s) ,Total: %d line(s)' % ( len(lstF[1]),intTotalLines ) )

#文件合并,将目录下的所有文件按行合并（自动处理文件开头与结尾）
#最终结果输出到参数2指定的文件中；
def filemerge (path,outfile):
    pass
    if not outfile:
        return 0
    lstF = getFiles(path)
    intTotalLines = 0
    strFline = ''
    with open(outfile,'a',encoding='utf-8') as fw:
        for fname in lstF[1] :
            txt = readtxtfile(fname)
            lstLines = txt.splitlines()
            intLines = len(lstLines)
            if intTotalLines == 0:
                strFline = lstLines[0] #记录下第一个文件的首行
            else:
                #第2个文件开始,如果首行与第一个文件相同，则删除第一行
                if lstLines[0]==strFline:
                    lstLines = lstLines[1:]
                    txt = '\n'.join(lstLines)
            if intTotalLines>1: #第2个文件开始加换行,否则开头会有一个空行
                fw.write(sysCRLF())
            fw.write(txt)
            intTotalLines += intLines
            #print('Processing file:%s ==> %d lines ' % (fname,intLines), end = '')
            print('Processing file:%s ==> %d lines ' % (fname,intLines))
    print('\n%d File(s) ,Total: %d line(s)' % (len(lstF[1]),intTotalLines ) )
    print('merge files to %s' % outfile)

#命令行主程序
def maincli ():
    pass
    if len(sys.argv)==1:
        print('文件批量处理工具 v0.1.3')
        print('可对目录下的文件进行批量处理: 以下参数的顺序可以根据实际需要调整 ')
        print('    [fmt]              文本清洗处理，包括：删除HTML代码，删除空格，空行等；')
        print('    [pre]              文本预处理，删除文件中的空格，空行，并按句子分行,插入标签列，加首行')
        print('    [same [0|1]]       查找内容相同的文件，改名(0)或者删除(1),默认为0')
        print('    [del  [0|1]]       查找空文件，改名(0)或者删除(1),,默认为0')
        print('    [ren  [N]]         从N开始批量重命名，默认起始编号为1')
        print('    [line ]            统计文件行数')
        print('    [count]            统计文件标签情况')
        print('    [check]            检查数据文件格式化情况')
        print('    [sample]           对数据进行随机抽样')
        print('    [merge outfile]    合并文件;outfile为合并后文件,未指定则自动命名为 merge+YYYYMMDDHHNNSS+随机.txt')
        print('    [split [Scale]]    将指定数据文件按比例拆分成三个数据集，默认为6,2,2')
        print('使用说明:')
        print('usage: python filetools.py workdir [p|pre] [s|same [1]] [d|del [1]] [r|ren [N]] [split [Scale]]')
        sys.exit(0)

    work_dir = sys.argv[1]
    #print('目录或者文件:%s' % work_dir)
    if not os.path.exists(work_dir):
        print('目录%s不存在，请检查!' % work_dir)
        sys.exit(0)
    
    lstPara = sys.argv[2:]

    for i in range(len(lstPara)):
        strPar = lstPara[i]
        #print(strPar)
        if strPar in ['pre']:
            strNextPar = lstPara[i+1] if i+1<len(lstPara) else '0'
            if not strNextPar in ['0','1']:
                strNextPar = '0'
            #预处理
            print('正在预处理:')
            pre_process (work_dir,strNextPar)


        if strPar in ['same']:
            strNextPar = lstPara[i+1] if i+1<len(lstPara) else ''
            if strNextPar.isnumeric():
                intNextPar = int(strNextPar)
                #print('正在删除重复文件: 参数 %s' % (intNextPar))
            else:
                intNextPar = 0
                #print('正在删除重复文件:无参数')
            #重复文件检查
            print('正在删除重复文件:')
            FindSameFile (work_dir, intNextPar)

        if strPar in ['del']:
            strNextPar = lstPara[i+1] if i+1<len(lstPara) else ''
            if strNextPar.isnumeric():
                intNextPar = int(strNextPar)
                print('正在删除空文件: 参数 %s' % (intNextPar))
            else:
                intNextPar = 0
                print('正在删除空文件:无参数')
            #空文件检查
            print('正在删除空文件:')
            delblankfile (work_dir,intNextPar)

        if strPar in ['ren']:
            strNextPar = lstPara[i+1] if i+1<len(lstPara) else ''
            if strNextPar == '1':
                intNextPar = 1
                #print('命令ren, 参数 %s' % (intNextPar))
            else:
                intNextPar = 0
                #print('命令ren, 无参数')
            
            #批量重命名
            print('正在批量重命名文件:')
            brename (work_dir,intNextPar)

        if strPar in ['line']:
            #批量统计行数
            print('正在批量统计行数:')
            linesCount (work_dir)
        
        #文件内容清洗
        if strPar in ['fmt']:
            print('正在批量清洗文本内容:')
            pre_format (work_dir)

        #客服内容提取
        if strPar in ['kf']:
            print('正在批量提取客服内容:')
            pre_kf (work_dir)

        #专家文件分类
        if strPar in ['expertclass']:
            print('正在进行专家文本分类处理:')
            expert_class (work_dir)

        #标注数据检查
        if strPar in ['check']:
            strNextPar = lstPara[i+1] if i+1<len(lstPara) else '0'
            if not strNextPar in ['0','1']:
                strNextPar = '0'
            #print('正在批量检查数据:')
            #DatCheck (work_dir)
            return pd_datCheck(work_dir, int(strNextPar))

        #标注数据随机化
        if strPar in ['sample']:
            return pd_datSample(work_dir)

        if strPar in ['count']:
            strNextPar = lstPara[i+1] if i+1<len(lstPara) else ''
            if strNextPar == '1':
                intNextPar = 1
            else:
                intNextPar = 0
            #批量统计标签
            print('正在批量统计标签:')
            LabelCount (work_dir,intNextPar)
        
        #file merge
        if strPar in ['merge']:
            strNextPar = lstPara[i+1] if i+1<len(lstPara) else ''
            if not strNextPar:
                strNextPar = autoFileName('merge','.txt')
                #print('正在合并文件,自动生成文件名：%s' % (strNextPar))
            
            #批量重命名
            print('正在合并文件:')
            filemerge (work_dir,strNextPar)

        if strPar in ['split']:
            strNextPar = lstPara[i+1] if i+1<len(lstPara) else '6,2,2'
            #拆分数据集
            print('正在拆分数据集:')
            print('数据集:%s' % work_dir)
            print('拆分比例:%s' % strNextPar)
            splitset(work_dir,str2List(strNextPar))



if __name__ == '__main__':
    pass
    maincli()
    
