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

time_sleep = 5

insert_count = 0

# 失败处理 超过20次休眠90秒
fail_count = 0
fail_count_limit = 10
fail_sleep = 100

headers = {
    "Accept"	:"*/*",
    "Accept-Encoding"	:"gzip, deflate",
    "Accept-Language"	:"en-US,en;q=0.5",
    "Connection"	:"keep-alive",
    "Content-Length"	:"109",
    "Content-Type"	:"application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie":"Hm_lpvt_d9f99ed0a40e413ff5b942f6723d305e=1548809153;Hm_lvt_d9f99ed0a40e413ff5b942f6723d305e=1548311420,1548749185;huazhan_log=d6101ec6b0aa6663c40f3f1743dff411;PHPSESSID=oscm9a5mrdnkm4l37br1jtnrk6",
    "Host"	:"yun.ihuazhan.net",
    "Referer"	:"http://yun.ihuazhan.net/Index/enterprise?type=1&keyword=%E7%89%A9%E8%81%94%E7%BD%91",
    "User-Agent"	:"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0",
    "X-Requested-With"	:"XMLHttpRequest"
}

#proxies for inside intel
proxies = {"http": "http://child-prc.intel.com:913",
               "https": "http://child-prc.intel.com:913"}

db_username = "root"
db_password = "misakaxindex"
db_dbname = "findcompany"

## 找出最合适的联系人 ##
## 经理 重要度 +2
## 手机 重要度 +1
## 法人 重要度 -1 
def find_main_contect(contects):
    for item in contects:
        item['priority'] = 0

    for item in contects:
        position = item.get("position", "")
        if position == "" or position.find("法人") != -1:
            item["priority"] -= 1
        if position.find("经理") != -1:
            item['priority'] += 1


    for item in contects:
        phone = item.get('phone', "")
        if phone != "":
            item['priority'] += 1
        
    max_priority = contects[0]['priority']
    max_priority_contect = 0
    i = 0
    while i < len(contects):
        if contects[i]['priority'] > max_priority:
            max_priority = contects[i]['priority']
            max_priority_contect = i
        i += 1

    return contects[max_priority_contect]

class mysql_huazhan:
    def __init__(self, user, password, database):
        self.db = pymysql.connect(host='localhost',
                                  user=user,
                                  passwd=password,
                                  db=database,
                                  charset='utf8')
        self.cursor = self.db.cursor()
    
    def insert_company(self, detail, contects, exhibitions, raw):
        id = detail.get('id', "")
        name = detail.get('name', "")
        tag = detail.get('trades', "")
        location = detail.get('areas', "")
        address = detail.get('address', "")
        url = detail.get('url', "")
        # 产品介绍 #
        product = detail.get('prodcut', "")
        # regcaptal 注册资本#
        regcapital = detail.get("regcapital","")

        # 正向搜索有手机号的联系人
        contect_main = find_main_contect(contects)
        
        contect_main_name = contect_main.get('name', "")
        contect_main_phone = contect_main.get('phone', "")
        contect_main_tel = contect_main.get('tel', "")
        contect_main_qq = contect_main.get('qq', "")
        contect_main_email = contect_main.get('email', "")
        contect_main_position = contect_main.get('position', "")

        contect_all_json = json.dumps(contects)
        exhibitions_json = json.dumps(exhibitions)

        sql = """INSERT INTO huazhan_company (huazhan_id, company, tag, location, address, homePage, product, regCapital, contectName, contectPosition, contectPhone, contectTel, contectQq, contectEmail, contectAllJson, exhibitionJson, raw) 
                    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}')""" \
                    .format(id, name, tag, location, address, url, product, regcapital, contect_main_name, contect_main_position, contect_main_phone, contect_main_tel, contect_main_qq, contect_main_email, contect_all_json, exhibitions_json, raw)
        self.cursor.execute(
            "SELECT COUNT(huazhan_id) FROM huazhan_company WHERE huazhan_id LIKE '{0}';".format(id))
        if self.cursor._rows[0] != (0,):
            return 0

        try:
            self.cursor.execute(sql)
            self.db.commit()
            return 1
        except:
            return 0


db = mysql_huazhan(db_username, db_password, db_dbname)

def huazhan_search_company_detail(id):
    url = "http://yun.ihuazhan.net/Index/eDetail"
    global headers
    global proxies
    data = {
        "id":   id,
        "state":	2,
        "requestType":	"searchEnterprise"
    }

    try:
        r = requests.post(url, data=data, headers=headers, proxies=proxies)
        time.sleep(time_sleep)
    except BaseException as err:
        print("time out "+ err)

    r.encoding = 'utf-8'
    rdata = json.loads(r.text)

    global db
    ret = db.insert_company(rdata['detail'], rdata['cur'], rdata['pro'], r.text)
    global insert_count
    if ret:
        insert_count += 1
        print("company inserted! total "+ str(insert_count))

def huazhan_search_company_list(keyword, page, sort):
    url = "http://yun.ihuazhan.net/Index/enterpriseAjax"
    global headers
    headers["Referer"] = "http://yun.ihuazhan.net/Index/enterprise?type=1&keyword=" + parse.quote(keyword)
    data = {
        "keyword":	keyword,
        "tradeid":	"",
        "areaid":	"",
        "companys":	10,
        "sort":	sort,
        ## islink=1 限定有联系方式的公司 ##
        "islink":	1,
        "isurl":	0,
        "istrack":	0,
        "special":	0,
        "type":	1,
        "pagecode":	page
    }
    global proxies

    try:
        r = requests.post(url, data=data, headers=headers, proxies=proxies)
        time.sleep(time_sleep)
    except ConnectionError as err:
        print("ConnectionError: '{0}'".format(err))

    r.encoding = 'utf-8'
    rdata = json.loads(r.text)

    for item in rdata["data"]:
        huazhan_search_company_detail(item["id"])

## ========================
## |  华展云搜索主程序       |
## | keyword 关键词        |
## | page_start 从哪页开始  |
## | page_end 到哪页结束    |
## | sortType = 1 综合排序  |
## | sortType = 2 时间排序  |
## ========================
def huazhanyun(keyword, page_start, page_end, sortType):
    i = page_start
    while i < page_end:
        huazhan_search_company_list(keyword, i, sortType)
        i += 1


areaid = {
    '北京':"e3EbEKiJ",
    '上海':"eTKbTKiz",
    '广东':"e8EcAEz6",
    '陕西':"e8bEEEmJ",
    '香港':"eww8AEzN",
    '海南':"eTAT8Ei6",
    '湖北':"ecKw8EiN",
    '辽宁':"eKdKEEmz",
    '安徽':"ebwwEEmN",
    '吉林':"eKETKEm6"

}

if __name__ == "__main__":
    proxies={
        "http":None,
        "https":None
    }
    huazhanyun("物联网", 0, 1000, 1)
