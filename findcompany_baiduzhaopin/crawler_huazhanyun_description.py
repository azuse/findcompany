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
db_username = "root"
db_password = "misakaxindex"
db_dbname = "findcompany"

db = pymysql.connect(host='localhost',
                    user=db_username,
                    passwd=db_password,
                    db=db_dbname,
                    charset='utf8')
cursor = db.cursor()

sql = "SELECT id,company,address FROM company ORDER BY id DESC ;"

cursor.execute(sql)

data = cursor.fetchall()

config = json.load(open("crawler_config.json"))

print_method = config["DEFAULT"]['print_method']
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
time_sleep = int(config['BAIDU']['time_sleep'])
headers_baidu = config['BAIDU']['headers']
bd = baiduzhaopin(headers=headers_baidu, proxies=proxies, time_sleep=time_sleep, logfileHandler=logfile, print_method=print_method)

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
    if ret != -1:
        for row in ret:
            try:
                pprint.pprint(row.get("companydescription",""))
                sql = "UPDATE company SET description = '" + row.get("companydescription","").replace("'","") + "' WHERE id = " + str(id) +  ";"
                cursor.execute(sql)
                db.commit()
            except:
                print("Unexpected error:", sys.exc_info()[0])