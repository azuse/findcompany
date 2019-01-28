#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib
from urllib import parse
# from django.utils.http import urlquote
import requests
import json
import pymysql
import time
import random
import string
from bs4 import BeautifulSoup
import re
import sys

time_sleep = 1

# 失败处理 超过20次休眠90秒
fail_count = 0
fail_count_limit = 10
fail_sleep = 900

# 百度招聘mysql插入函数


class mysql_baiduzhaopin:

    def __init__(self, user, password, database):
        self.db = pymysql.connect(host='localhost',
                                  user=user,
                                  passwd=password,
                                  db=database,
                                  charset='utf8')
        self.cursor = self.db.cursor()

    def insert(self, data, queryword):
        sid = data.get('@sid', "")

        name = data.get("@name", "")
        company = data.get("company", "")
        city = data.get("city", "")

        depart = data.get("depart", "")

        education = data.get("education", "")
        employertype = data.get("employertype", "")
        experience = data.get("experience", "")

        first_level_label = data.get("first_level_label", "")
        second_level_label = data.get("second_level_label", "")
        third_level_label = data.get("third_level_label", "")

        label = first_level_label + ',' + second_level_label + ',' + third_level_label

        jobfirstclass = data.get("jobfirstclass", "")
        jobsecondclass = data.get("jobsecondclass", "")
        jobthirdclass = data.get("jobthirdclass", "")

        jobclass = jobfirstclass + ',' + jobsecondclass + ',' + jobthirdclass

        salary = data.get("salary", "")

        location = data.get("location", "")

        url = data.get("pc_url", "")

        companyaddress = data.get("companyaddress", "")
        companydescription = data.get("companydescription", "")
        companysize = data.get("companysize", "")
        company_id = data.get("company_id", "")

        rowdata = json.dumps(data)
        sql = """INSERT INTO baiduzhaopin (sid, jobName, company, city, depart, education, employerType, experience, label, jobClass, salary, location, url, companyAddress, companyDescription, companySize, rowData, queryWord, companyId) VALUES
                                        ('{0}', '{1}'  ,'{2}'   ,'{3}',  '{4}' , '{5}'    , '{6}'       , '{7}'     , '{8}', '{9}'   , '{10}', '{11}'  ,'{12}','{13}'        , '{14}'            , '{15}'     , '{16}' , '{17}'   ,'{18}');""" \
                                 .format(sid, name, company, city, depart, education, employertype, experience, label, jobclass, salary, location, url, companyaddress, companydescription.replace("'", ""), companysize, rowdata, queryword, company_id)
        self.cursor.execute(
            "SELECT COUNT(sid) FROM baiduzhaopin WHERE sid LIKE '{0}';".format(sid))
        if self.cursor._rows[0] != (0,):
            return 0

        try:
            self.cursor.execute(sql)
            self.db.commit()
            return 1
        except:
            return 0

    # 将查到的company官网链接插入数据库
    def insertCompany(self, company, cid, url):
        sql = """INSERT INTO company (cid, company, url) VALUES ('{0}', '{1}'  ,'{2}');""" .format(
            cid, company, url)
        self.cursor.execute(
            "SELECT COUNT(cid) FROM company WHERE cid LIKE '{0}';".format(cid))
        if self.cursor._rows[0] != (0,):
            return 0

        try:
            self.cursor.execute(sql)
            self.db.commit()
            return 1
        except:
            return 0


db_username = "root"
db_password = "misakaxindex"
db_dbname = "findcompany"
db = mysql_baiduzhaopin(db_username, db_password, db_dbname)


def fail():
    global fail_count
    global fail_count_limit
    global fail_sleep
    fail_count = fail_count + 1
    if fail_count >= fail_count_limit:
        print("fail too much, going to sleep a while")
        time.sleep(fail_sleep)
        fail_count = 0


def getToken(query, city):
    global time_sleep

    print("获取token")
    url = "http://zhaopin.baidu.com/quanzhi?query=" + \
        parse.quote(query)+"&city="+parse.quote(city)
    headers = {"Accept": "*/*",
               "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                   "Connection": "keep-alive",
                   "Cookie": "BAIDUID=D218FD911DA27FA9E5C8A9B6B3F62C92:FG=1; BIDUPSID=D218FD911DA27FA9E5C8A9B6B3F62C92; PSTM=1548381180; delPer=0; PSINO=5; H_PS_PSSID=26525_1443_21105_28328_22158",
                   "DNT": "1",
                   "Host": "zhaopin.baidu.com",
                   "Referer": "http://zhaopin.baidu.com/quanzhi?query="+parse.quote(query)+"&city="+parse.quote(city),
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36}"
               }

    proxies = {"http": "http://child-prc.intel.com:913",
               "https": "http://child-prc.intel.com:913"}
    while 1:
        try:
            r = requests.get(url, headers=headers, proxies=proxies)
            time.sleep(time_sleep)

            break
        except:
            print("获取token时网络错误,重试")
            fail()
            time.sleep(time_sleep)

            continue
    index = r.text.index("window.zp_pc_nekot")
    test = r.text[index:index+100]
    token = r.text[index+22:index+66]
    # reverse token
    token = token[::-1]
    token = parse.quote(token)
    url = "http://zhaopin.baidu.com/api/news?type=5&token="+token
    try:
        r = requests.get(url, proxies=proxies)
        time.sleep(time_sleep)

    except:
        pass
    print("new token:"+token)
    return token

# =========================
# | 百度招聘api查询函数      |
# | query   查询关键词      |
# | num     查询多少个职位   |
# =========================


def baiduzhaopin(query, city, num):
    # rn意义不明 也许是每次返回的结果数？
    rn = 10
    # pn返回第pn个开始的结果 pn/10相当于 页
    pn = 10
    token = getToken(query, city)
    while pn < num:

        # #####IMPORTANT#####
        # token 必须要有 不让强制搜索"招聘",但是token的值无所谓
        # api后台有校验,校验过程不清楚,校验失败query会强制变成"招聘"
        # 即使token设置正确，抓取数据的频率过高也会被ban，ban的应该是ip

        url = "http://zhaopin.baidu.com/api/qzasync?query=" + parse.quote(query) + "&city=" + parse.quote(
            city) + "&is_adq=1&pcmod=1&token=" + token + "&pn=" + str(pn) + "&rn=" + str(rn) + "&sort_type=1&sort_key=5"

        headers = {"Accept": "*/*",
                   "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                   "Connection": "keep-alive",
                   "Cookie": "BAIDUID=D218FD911DA27FA9E5C8A9B6B3F62C92:FG=1; BIDUPSID=D218FD911DA27FA9E5C8A9B6B3F62C92; PSTM=1548381180; delPer=0; PSINO=5; H_PS_PSSID=26525_1443_21105_28328_22158",
                   "DNT": "1",
                   "Host": "zhaopin.baidu.com",
                   "Referer": "https://zhaopin.baidu.com/quanzhi?query="+parse.quote(query)+"&city="+parse.quote(city),
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36}"
                   }

        proxies = {"http": "http://child-prc.intel.com:913",
                   "https": "http://child-prc.intel.com:913"}

        try:
            r = requests.get(url, proxies=proxies, headers=headers)

            global time_sleep
            time.sleep(time_sleep)
        except:
            print("request timeout")
            continue
        r.encoding = 'utf8'

        rdata = json.loads(r.text)

        global db
        if rdata['data']['errno'] == -1:
            print("数据获取失败,可能是已经取得了所有结果")
            pn = pn + 10
            return

        hilight = rdata['data']['hilight'].split("\x00")[0]
        if hilight != query:
            print("token失效,或抓取受到限制")
            fail()
            token = getToken(query, city)
            continue

        # 新插入的条目计数
        inserted = 0
        for item in rdata['data']['disp_data']:
            ret = db.insert(item, query)
            if ret == 1:
                inserted = inserted + 1
        print("pn="+str(pn)+",total:"+str(num)+",inserted="+str(inserted))
        pn = pn + 10

    return "查询结束"


# ==================================
# |使用百度百聘的company id寻找公司信息 |
# ==================================
def baiducompany(cid, company):
    url = "http://zhaopin.baidu.com/company?query=" + \
        cid+"&page=registration&city=%E4%B8%8A%E6%B5%B7"

    headers = {"Accept": "*/*",
               "Accept-Encoding": "gzip, deflate, br",
                   "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                   "Connection": "keep-alive",
                   "Cookie": "BAIDUID=D218FD911DA27FA9E5C8A9B6B3F62C92:FG=1; BIDUPSID=D218FD911DA27FA9E5C8A9B6B3F62C92; PSTM=1548381180; delPer=0; PSINO=5; H_PS_PSSID=26525_1443_21105_28328_22158",
                   "DNT": "1",
                   "Host": "zhaopin.baidu.com",
                   "Referer": "https://zhaopin.baidu.com/quanzhi?query=%E8%AE%A1%E7%AE%97%E6%9C%BA&city=%E4%B8%8A%E6%B5%B7",
                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36}"
               }

    proxies = {"http": "http://child-prc.intel.com:913",
               "https": "http://child-prc.intel.com:913"}

    try:
        r = requests.get(url, proxies=proxies)

        global time_sleep
        time.sleep(time_sleep)
    except:
        print("request timeout")

    # r.encoding = 'utf8'
    soup = BeautifulSoup(r.text, features="html.parser")

    ret = soup.select('div:contains("企业官网").line-equal-item')
    if len(ret) == 0:
        print(company + " not found")
        return -1
    companyUrl = ret[0].text.split("企业官网")[1]

    ret = soup.select('title')
    companyName = ret[0].text.split("-企业名片-")[0]

    global db
    db.insertCompany(companyName, cid, companyUrl)

    print(companyName + companyUrl + " inserted!")

# 自动查找百度招聘数据库里的公司官网


def findCompanyUrl():
    sql = "SELECT `companyId`, `company` FROM `baiduzhaopin` WHERE `companyId` NOT IN (SELECT `cid` FROM `company`) GROUP BY `companyId`,`company` ORDER BY `company` DESC"
    global db
    db.cursor.execute(sql)
    db.db.commit()
    results = db.cursor.fetchall()
    for row in results:
        baiducompany(row[0], row[1])



if __name__ == "__main__":
    if(sys.argv[1] == "zhaopin"):
        ret = baiduzhaopin("计算机视觉", "深圳", 1000)
        print(ret)
        ret = baiduzhaopin("计算机", "深圳", 1000)
        print(ret)
        ret = baiduzhaopin("物联网", "深圳", 1000)
        print(ret)
        ret = baiduzhaopin("智能", "深圳", 1000)
        print(ret)
        ret = baiduzhaopin("无人", "深圳", 1000)
        print(ret)
        ret = baiduzhaopin("高科技", "深圳", 1000)
        print(ret)

        ret = baiduzhaopin("计算机视觉", "北京", 1000)
        print(ret)
        ret = baiduzhaopin("计算机", "北京", 1000)
        print(ret)
        ret = baiduzhaopin("物联网", "北京", 1000)
        print(ret)
        ret = baiduzhaopin("智能", "北京", 1000)
        print(ret)
        ret = baiduzhaopin("无人", "北京", 1000)
        print(ret)
        ret = baiduzhaopin("高科技", "北京", 1000)
        print(ret)

        ret = baiduzhaopin("计算机视觉", "上海", 1000)
        print(ret)
        ret = baiduzhaopin("计算机", "上海", 1000)
        print(ret)
        ret = baiduzhaopin("物联网", "上海", 1000)
        print(ret)
        ret = baiduzhaopin("智能", "上海", 1000)
        print(ret)
        ret = baiduzhaopin("无人", "上海", 1000)
        print(ret)
        ret = baiduzhaopin("高科技", "上海", 1000)
        print(ret)
    elif(sys.argv[1] == "company"):
       while 1:
            findCompanyUrl()
        
    else:
        print("python3 baiduzhaopin.py company -> get company homesite url")
        print("python3 baiduzhaopin.py zhaopin -> get zhaopin information from baidu zhaopin")
