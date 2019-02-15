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

time_sleep = 10

## 3个功能
## - 融合华展云和百度百聘
## - 从百度找官网
## - 从企名片找官网

def urlparse(url):
    url = url.replace("http://","")
    url = url.replace("https://","")
    url = url.replace("/","")
    return url

### 从企名片抓取官网
def get_homepage_from_qimingpian(companyName):
    pass


### 将华展云的公司主页和百度百聘的公司主页表融合
def merge_huazhanyun_Homepages_with_baiduzhaopin_Homepages():
    sql = "SELECT MAX(id) FROM huazhan_company;"
    
def baidu_search_homepage(company):
    url = "http://www.baidu.com/s?wd="+company+"%20官网"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    ret = soup.select("div[class='f13'] > a")
    if len(ret) == 0:
        print(company + " not found")
        return -1
    if ret[0].text.find("\xa0") != -1:
        companyUrl = ret[0].text.split("\xa0")[0]
        return urlparse(companyUrl)
    else:
        return ""


def findCompanyZhaopin(company, proxies, headers):
    global time_sleep

    print("info: 搜索公司: "+ company)
    url = "http://zhaopin.baidu.com/quanzhi?query=" + parse.quote(company)
    
    while 1:
        try:
            r = requests.get(url, headers=headers, proxies=proxies)
            # time.sleep(time_sleep)

            break
        except:
            print("error: 搜索公司时网络错误,退出")
            fail()
            # time.sleep(time_sleep)

            continue
    soup = BeautifulSoup(r.text, features="html.parser")

    city = soup.select('div.inlineblock div.detail span')[0].text
    

db_username = "root"
db_password = "misakaxindex"
db_dbname = "findcompany"

db = pymysql.connect(host='localhost',
                     user=db_username,
                     passwd=db_password,
                     db=db_dbname,
                     charset='utf8')
cursor = db.cursor()

sql = "SELECT id,company FROM huazhan_company"

cursor.execute(sql)

data = cursor.fetchall()

import crawler_baiduzhaopin

for item in data:
    
    id = item[0]
    company = item[1]
    
    
    try:
        proxies = {
            "http": "http://child-prc.intel.com:913",
            "https": "http://child-prc.intel.com:913"
        }
        crawler_baiduzhaopin.proxies = {
            "http": "http://child-prc.intel.com:913",
            "https": "http://child-prc.intel.com:913"
        }
        headers = {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                        "Connection": "keep-alive",
                        "Cookie": "BAIDUID=D218FD911DA27FA9E5C8A9B6B3F62C92:FG=1; BIDUPSID=D218FD911DA27FA9E5C8A9B6B3F62C92; PSTM=1548381180; delPer=0; PSINO=5; H_PS_PSSID=26525_1443_21105_28328_22158",
                        "DNT": "1",
                        "Host": "zhaopin.baidu.com",
                        "Referer": "https://zhaopin.baidu.com/quanzhi?query=%E8%AE%A1%E7%AE%97%E6%9C%BA&city=%E4%B8%8A%E6%B5%B7",
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36}"
                    }
        print(findCompanyZhaopin(company,proxies,headers))
    except:
        print("Unexpected error:", sys.exc_info()[0])

    # sql = "UPDATE huazhan_company SET homePage = '{0} WHERE id = {1};';".format(url,id)
    # cursor.execute(sql)
    # db.commit()

