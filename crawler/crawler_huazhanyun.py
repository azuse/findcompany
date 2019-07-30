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
from optparse import OptionParser
import configparser, os
import pprint

insert_count = 0
time_sleep = 20

def urlparse(url):
    url = url.replace("http://","")
    url = url.replace("https://","")
    url = url.replace("/","")
    return url

def writePID():
    pidfile = open("mainPID.txt", "w", encoding="utf8")
    pidfile.write(str(os.getpid()))
    pidfile.write("\n")
    pidfile.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    pidfile.flush()
    pidfile.close()

logfile = open("crawler_log.txt", "w", encoding="utf8")
def print(text, text2=""):
    if print_method == "terminal":
        sys.stdout.write(str(text))
        sys.stdout.write(str(text2))
        sys.stdout.write("\n")
    else:
        logfile.write(str(text))
        logfile.write(str(text2))
        logfile.write("\n")
        logfile.flush()

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
        self.user = user
        self.password = password
        self.database = database
        
    
    def insert_company(self, detail, contects, exhibitions, raw):
        id = detail.get('id', "")
        name = detail.get('name', "")
        tag = detail.get('trades', "")
        location = detail.get('areas', "")
        address = detail.get('address', "")
        url = detail.get('url', "")
        if(url != None):
            url = urlparse(url)
        # 产品介绍 #
        product = detail.get('prodcut', "")
        # regcaptal 注册资本#
        regcapital = detail.get("regcapital","")

        # 正向搜索有手机号的联系人
        if contects != None:
            contect_main = find_main_contect(contects)
        else :
            contect_main = dict()

        contect_main_name = contect_main.get('name', "")
        contect_main_phone = contect_main.get('phone', "")
        contect_main_tel = contect_main.get('tel', "")
        contect_main_qq = contect_main.get('qq', "")
        contect_main_email = contect_main.get('email', "")
        contect_main_position = contect_main.get('position', "")

        contect_all_json = json.dumps(contects)
        exhibitions_json = json.dumps(exhibitions)

        sql = """INSERT INTO company (huazhan_id, company, tag, location, address, homePage, product, regCapital, contectName, contectPosition, contectPhone, contectTel, contectQq, contectEmail, contectAllJson, exhibitionJson, raw) 
                    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}')""" \
                    .format(id, name, tag, location, address, url, product, regcapital, contect_main_name, contect_main_position, contect_main_phone, contect_main_tel, contect_main_qq, contect_main_email, contect_all_json, exhibitions_json, raw)
        self.db = pymysql.connect(host='localhost',
                                  user=self.user,
                                  passwd=self.password,
                                  db=self.database,
                                  charset='utf8')
        self.cursor = self.db.cursor()
        
        self.cursor.execute(
            "SELECT COUNT(huazhan_id) FROM company WHERE huazhan_id LIKE '{0}';".format(id))
        if self.cursor._rows[0] != (0,):
            return 0

        try:
            self.cursor.execute(sql)
            self.db.commit()
            self.db.close()
            return 1
        except:
            self.db.close()
            return 0


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
        r = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=time_out)
        time.sleep(time_sleep)
    except ConnectionError as err:
        print("ConnectionError in huazhan_search_company_detail: '{0}'".format(err))
        return 0
    except:
        print("Unexpected error in huazhan_search_company_detail:", sys.exc_info()[0])
        return 0


    print("-------------------------------enterprise detail 200")
    r.encoding = 'utf-8'
    rdata = json.loads(r.text)

    global db
    ret = db.insert_company(rdata['detail'], rdata['cur'], rdata['pro'], r.text)
    global insert_count
    if ret:
        insert_count += 1
        print("company inserted! total "+ str(insert_count))
        global tmpcursor
        global tmpdb
        tmpcursor.execute("UPDATE update_history SET result_count = {0} WHERE addId = {1};".format(insert_count, addId))
        tmpcursor.fetchall()
        tmpdb.commit()
    else :
        print("company already exist")
    return ret


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
        ## isurl=1 由企业网址的公司
        "isurl":	1,
        "istrack":	0,
        "special":	0,
        "type":	1,
        "pagecode":	page
    }
    global proxies

    try:
        r = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=time_out)
        time.sleep(time_sleep)
    except ConnectionError as err:
        print("ConnectionError in huazhan_search_company_list: '{0}'".format(err))
        return 0
    except:
        print("Unexpected error in huazhan_search_company_list:", sys.exc_info()[0])
        pprint.pprint(r.text)
        return 0

    print("-------------------------------enterprise index 200---------page "+ str(page))
    r.encoding = 'utf-8'
    if r.status_code == 403:
        print("error: site return 403")
        sys.exit(1)
    print(r.text)
    try:
        rdata = json.loads(r.text)
    except:
        return 0 
    inserted = 0
    if not rdata["data"]:
        inserted = -1
        return inserted
    for item in rdata["data"]:
        ret = huazhan_search_company_detail(item["id"])
        inserted += ret
    return inserted

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
    inserted = 0
    while i < page_end:
        if sortType == "time":
            ret = huazhan_search_company_list(keyword, i, 2)
            if ret == -1:
                print("last page")
                break
            inserted += ret
            i += 1
        if sortType == "auto":
            if ret == -1:
                print("last page")
                break
            ret = huazhan_search_company_list(keyword, i, 1)
            inserted += ret
            i += 1
    return "查找结束: {0} {1} {2} {4} 插入结果: {4}".format(keyword, page_start, page_end, sortType, inserted)

def huazhan_login(username, password):
    url = "http://yun.ihuazhan.net/Login/loginCheck"
    global headers
    data = {
        "userName": username,
        "password": password
    }
    r = requests.post(url, data=data, headers=headers)
    print(r.text)

# 华展云中使用的areaid，实际爬虫中并没用到
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
    writePID()
    print_method = "terminal"


    proxies={
        "http":None,
        "https":None
    }

    usage = "usage: python3 crawler_huazhanyun.py "
    parser = OptionParser()
    parser.add_option("-p", "--proxy", help="select a proxy", metavar="intel / socks5 / noproxy", default="intel", dest="proxy_select")
    parser.add_option("-c","--config", help="select a config file", metavar="crawler_config.json", default="crawler_config.json", dest="config_path")
    parser.add_option("-t","--timesleep", help="timesleep seconds", metavar="10", default=-1, dest="time_sleep")
    (opt, args) = parser.parse_args()

    print('info: using config file: '+ opt.config_path)
    config = json.load(open(opt.config_path, encoding="utf8"))
    print_method = config["DEFAULT"]['print_method']
    time_out = config['DEFAULT']['time_out']
    ######## HUAZHAN ##########
    if opt.time_sleep == -1:
        time_sleep = int(config['HUAZHAN']['time_sleep'])
    else:
        time_sleep = int(opt.time_sleep)

    keywords = config['HUAZHAN']['keywords']

    page_start = int(config['HUAZHAN']['page_start'])
    page_end = int(config['HUAZHAN']['page_end'])

    sort_type = config['HUAZHAN']['sort_type']
    ######## MYSQL #########
    db_username = config['MYSQL']['db_username']
    db_password = config['MYSQL']['db_password']
    db_dbname = config['MYSQL']['db_dbname']

    db = mysql_huazhan(db_username, db_password, db_dbname)
    tmpdb = pymysql.connect(host='localhost',
                    user=db_username,
                    passwd=db_password,
                    db=db_dbname,
                    charset='utf8')
    tmpcursor = tmpdb.cursor()

    tmpcursor.execute("SELECT MAX(addId) FROM update_history; ")
    rows = tmpcursor.fetchall()
    if(rows[0][0] == None):
        addId = 1
    else:
        addId = rows[0][0] + 1

    tmpcursor.execute("INSERT INTO `update_history` (`addId`, `date`, `type`, `result_count`) VALUES ({0}, CURRENT_TIMESTAMP, 2, {1});".format(addId, insert_count))
    rows = tmpcursor.fetchall()
    tmpdb.commit()

    #proxies for inside intel
    opt.proxy_select = config['DEFAULT'].get("proxy", opt.proxy_select)

    headers = config['HUAZHAN']['headers']
    username = config["HUAZHAN"]["username"]
    password = config["HUAZHAN"]["password"]


    if(opt.proxy_select == "intel"):
        print("info: using intel proxy")
        proxies = {"http": "http://child-prc.intel.com:913",
               "https": "http://child-prc.intel.com:913"}
    elif(opt.proxy_select == "socks5"):
        print("info: using socks5 proxy")
        proxies = {"http": "socks5://127.0.0.1:1080","https": "socks5://127.0.0.1:1080"}
    elif(opt.proxy_select == "noproxy"):
        print("info: using no proxy")
        proxies = {"http":None, "https": None}

    
    print("-----------    login in  -----------")
    huazhan_login(username, password)
    print("-----------start crawling-----------")
    i = 0
    ret = dict()
    for keyword in keywords:
        ret[i] = huazhanyun(keyword, page_start, page_end, sort_type)
        i+=1

    print("-----------crawl ended----------")
    pprint(ret)

def huazhan_login():
    url = "http://yun.ihuazhan.net/Login/loginCheck"
    
    headers={
            "Accept"	:"*/*",
            "Accept-Encoding"	:"gzip, deflate",
            "Accept-Language"	:"en-US,en;q=0.5",
            "Connection"	:"keep-alive",
            "Content-Length"	:"109",
            "Content-Type"	:"application/x-www-form-urlencoded; charset=UTF-8",
            
            "Cookie":"Hm_lpvt_d9f99ed0a40e413ff5b942f6723d305e=1548899666;Hm_lvt_d9f99ed0a40e413ff5b942f6723d305e=1548899205;huazhan_log=49a9ef170a32a16bbf7cdb60eaed0af5;PHPSESSID=79a5va20f9vc6e8raqc62q1uf3",
            "Host"	:"yun.ihuazhan.net",
            "Referer"	:"http://yun.ihuazhan.net/Index/enterprise?type=1&keyword=%E7%89%A9%E8%81%94%E7%BD%91",
            "User-Agent"	:"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0",
            "X-Requested-With"	:"XMLHttpRequest"
        }
    headers['Cookie'] = "PHPSESSID=79a5va20f9vc6e8raqc62q1uf3;"
    data = {
        "userName":"18100837642",
        "password":"intel@123"
    }
    r = requests.post(url, data=data, headers=headers)
    print(r.text)
