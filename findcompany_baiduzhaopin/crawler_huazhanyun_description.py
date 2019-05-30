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
from crawler_main_head import baiduzhaopin

def writePID():
    pidfile = open("mainPID.txt", "w")
    pidfile.write(str(os.getpid()))
    pidfile.write("\n")
    pidfile.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    pidfile.flush()
    pidfile.close()

logfile = open("crawler_log.txt", "w")
print_method = "terminal"

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

writePID()


config = json.load(open("crawler_config.json"))
print_method = config["DEFAULT"]['print_method']
time_out = config['DEFAULT']['time_out']
time_sleep = int(config['BAIDU']['time_sleep'])
headers_baidu = config['BAIDU']['headers']
db_username = config['MYSQL']['db_username']
db_password = config['MYSQL']['db_password']
db_dbname = config['MYSQL']['db_dbname']
db = pymysql.connect(host='localhost',
                    user=db_username,
                    passwd=db_password,
                    db=db_dbname,
                    charset='utf8')

cursor = db.cursor()

cursor.execute("SELECT MAX(addId) FROM company; ")
rows = cursor.fetchall()
if(rows[0][0] == None):
    addId = 1
else:
    addId = rows[0][0] + 1

insert_count = 0
cursor.execute("INSERT INTO `update_history` (`addId`, `date`, `type`, `result_count`) VALUES ({0}, CURRENT_TIMESTAMP, 3, {1});".format(addId, insert_count))
rows = cursor.fetchall()
db.commit()


sql = "SELECT id,company,location FROM company ORDER BY id DESC ;"
cursor.execute(sql)
data = cursor.fetchall()


if(config['DEFAULT'].get("proxy", "noproxy") == "intel"):
    print("info: using intel proxy")
    proxies = {"http": "http://child-prc.intel.com:913",
                "https": "http://child-prc.intel.com:913"}
elif(config['DEFAULT'].get("proxy", "noproxy") == "socks5"):
    print("info: using socks5 proxy")
    proxies = {"http": "socks5://127.0.0.1:1080",
                "https": "socks5://127.0.0.1:1080"}
elif(config['DEFAULT'].get("proxy", "noproxy") == "noproxy"):
    print("info: using no proxy")
    proxies = {"http": None, "https": None}


bd = baiduzhaopin(headers=headers_baidu, proxies=proxies, time_sleep=time_sleep, logfileHandler=logfile, print_method=print_method, time_out=time_out)

for item in data:
    id = item[0]
    company = item[1]
    location = item[2]
    cities = json.load(open("cities.json"))
    for city in cities['cities']:
        if location.find(city['cityName']) != -1:
            location = city['cityName']
            break

    print("____"+company+"____"+location)
    ret = bd.baiduzhaopin(company, location)
    # 返回多个招聘结果 每个招聘结果都是同一个公司 公司简介应该是相同的
    if ret != -1:
        for row in ret:
            try:
                print(row.get("companydescription",""))
                sql = "UPDATE company SET description = '" + row.get("companydescription","").replace("'","") + "' WHERE id = " + str(id) +  ";"
                cursor.execute(sql)
                db.commit()
            except:
                print("Unexpected error:", sys.exc_info()[0])
        insert_count += 1
        cursor.execute("UPDATE update_history SET result_count = {0} WHERE addId = {1};".format(insert_count, addId))
        cursor.fetchall()
        db.commit()