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
    companyUrl = ret[0].text.split("/\\xa0")[0]
    return companyUrl

db_username = "root"
db_password = "misakaxindex"
db_dbname = "findcompany"

db = pymysql.connect(host='localhost',
                     user=db_username,
                     passwd=db_password,
                     db=db_dbname,
                     charset='utf8')
cursor = db.cursor()

sql = "SELECT id,url FROM companyHomepage WHERE url LIKE '%http%'"

cursor.execute(sql)

data = cursor.fetchall()

for item in data:
    
    id = item[0]
    url = item[1]
    url = url.replace("http://","")
    url = url.replace("https://","")
    url = url.replace("/","")
    
    
    try:
        sql = "UPDATE companyHomepage SET url = '{0}' WHERE id = {1}".format(url, id)
        cursor.execute(sql)
        db.commit()
    except:
        print("Unexpected error:", sys.exc_info()[0])

    # sql = "UPDATE huazhan_company SET homePage = '{0} WHERE id = {1};';".format(url,id)
    # cursor.execute(sql)
    # db.commit()

