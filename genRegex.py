#!/usr/bin/env python3
#coding:utf-8
# 2019/4/12 
__author__ = 'xmxoxo<xmxoxo@qq.com>'


'''
在基于自然语言的人机交互系统中，通常会定义一些语义模板来训练NLU (自然语言理解)模型，
比如下面的模板可以支持用户通过语音控制机器播放音乐：

放几首@{singer}的歌
播放一首@{singer}的歌
来一曲@{singer}的歌曲
来首@{singer}的音乐
来个@{singer}的流行音乐

其中"@{singer}"是个参数， 代表歌手，比如第一个模板可以匹配这样的用户query：“放几首刘德华的歌”。可以看到，同样是放歌，有很多种不同但相似的说法，但把他们一条一条单独列出来，编辑的成本会比较高， 而且会漏掉一些说法， 不严谨。实际上，上面的5个模板，可以用下面的语义模板表达式来表示：

<[播]放|来>[一|几]<首|曲|个>@{singer}的<歌[曲]|[流行]音乐>
其中包含中括号("[]") 、尖括号("<>") 和竖线("|")三种元素：

中括号代表其中的内容是可选的，比如"[歌]曲"，能匹配"歌"和"歌曲"；
尖括号代表其中的内容是必选的，比如"<播>放"， 能匹配"播放"；
括号是可以嵌套的；
竖线代表或的关系，即竖线分隔的内容是可替换的，
比如"<播放|来首>歌曲"能匹配"播放歌曲"和"来首歌曲"，
再如"[播放|来首]歌曲"能匹配"播放歌曲"，“来首歌曲"和"歌曲”(因为中括号里面是可选的，所以可以匹配歌曲) ；

竖线在其所属的括号内，优先级大于括号中的其他括号，
比如"<[播]放|来>首歌曲"，能匹配"播放首歌曲"，“放首歌曲"和"来首歌曲"；

竖线可以脱离括号独立存在，比如"在哪里|哪里有"，可以匹配"在哪里"和"哪里有"；

那么，给一个上述的语义模板表达式和用户的query，你能判断用户的quey是否能匹配这个表达式吗?

--------------------- 

作者：雪入红尘 
来源：CSDN 
原文：https://blog.csdn.net/xueruhongchen/article/details/89182387 
版权声明：本文为博主原创文章，转载请附上博文链接！

'''

import re

#根据文本规则生成正则表达式
#parm:
#    txt    用户的规则
#返回：
#    字符串，生成的正则表达式；
#测试用例:
# genRegex('<[播]放|来>[一|几]<首|曲|个>@{singer}的<歌[曲]|[流行]音乐>')
#return:
#   ^((播)?放|来)(一|几)?(首|曲|个)@\{singer\}的(歌(曲)?|(流行)?音乐)$ 
def genRegex (txt):
    pass
    ret = txt
    ret = ret.replace('{','\{')
    ret = ret.replace('}','\}')
    ret = ret.replace('[','(')
    ret = ret.replace(']',')?')
    ret = ret.replace('<','(')
    ret = ret.replace('>',')')
    ret = '^' + ret + '$'
    return ret

#对单条文本判断是否匹配规则
#参数：
#   strRegex    string,正则表达式
#   strTxt      string,待匹配的单条文本
#返回：
#   匹配返回True ，否则返回False
def testRule (strRegex,strTxt):
    pass
    try:
        #编译正则对象，参数：单行，多行，大小写
        reObj = re.compile(strRegex,re.S|re.U|re.M)
        searchObj = re.match(reObj,strTxt)
        #print(searchObj)
        return searchObj != None
    except Exception as e :
        return False

def doctest ():
    txt = [
    '放几首@{singer}的歌',
    '播放一首@{singer}的歌',
    '来一曲@{singer}的歌曲',
    '来首@{singer}的音乐',
    '来个@{singer}的流行音乐',
    '放首@{singer}的歌',
    '播放@{singer}的歌',
    '在哪里可以找到@{singer}的音乐',
    '哪里有@{singer}的歌曲',
    ]
    print('批量测试'.center(30,'-') )
    ruleTxt = '<[播]放|来>[一|几]<首|曲|个>@{singer}的<歌[曲]|[流行]音乐>'
    ruleRegex = genRegex(ruleTxt)
    print('规则文本：%s \n生成正则表达式：%s ' % ( ruleTxt,ruleRegex))
    print('-'*30)
    print('规则测试：')
    for x in txt:
        pass
        print('测试句子: %s 判断结果：%s' %(x , testRule(ruleRegex,x)) )        


if __name__ == '__main__':
    pass
    ruleTxt = '<[播]放|来>[一|几]<首|曲|个>@{singer}的<歌[曲]|[流行]音乐>'
    ruleRegex = genRegex(ruleTxt)
    print(ruleRegex)
    print(testRule (ruleRegex, '放几首@{singer}的歌'))

    doctest()
