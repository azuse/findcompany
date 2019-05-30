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

def writePID():
    pidfile = open("mainPID.txt", "w")
    pidfile.write(str(os.getpid()))
    pidfile.write("\n")
    pidfile.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    pidfile.flush()
    pidfile.close()

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


####################################
# 脉脉爬虫                           #
# @param company 需要抓取的公司名称   #
# @param headers 已经登录的cookies   #
# @param time_out 设置网络超时时间    #
####################################
def maimai(company, headers= {
        "cookie": """seid=s1551840667869; _buuid=506a7fbf-1b2f-481a-8031-85e007d99559; guid=GxMYBBsaGAQYGh4EGRxWBxgbHhwfExMaHRxWHBkEHRkfBUNYS0xLeQoSEwQSHR8ZBBoEGx0FT0dFWEJpCgNFQUlPbQpPQUNGCgZmZ35iYQIKHBkEHRkfBV5DYUhPfU9GWlprCgMeHHUcElIKUl9EQ2YKERsbcgIKGgQfBUtGRkNQRWc=; token="Q+TrGRMjLhgKkfDydWgiCN3OTEDcmCk5NReUcExsaSkZqFI82V6e6mK37MUFo07k8CKuzcDfAvoCmBm7+jVysA=="; uid="kBWdlFr7Q4Abh3QUS0c+rvAirs3A3wL6ApgZu/o1crA="; session=eyJ1IjoiMjIxMDIzODE5Iiwic2VjcmV0IjoiQmFOSXNQcFl6VEFSVDBGUkFKLW9fMU5vIiwibWlkNDU2ODc2MCI6ZmFsc2UsIl9leHBpcmUiOjE1NTE5Mjc3NTEwMDEsIl9tYXhBZ2UiOjg2NDAwMDAwfQ==; session.sig=ubREdw-SbtyPtXxyq_iUbxWnOek""",
    }, time_out = 20):
    url = "https://maimai.cn/search/contacts"
    data = {
        "count": 20,
        "page": 0,
        "query": company,
        "dist": 0,
        "searchTokens": "",
        "highlight": "true",
        "jsononly": 1,
        "pc": 1,
    }

    r = requests.get(url=url, params=data, headers=headers, proxies=proxies, timeout=time_out)
    jsondata = json.loads(r.text)
    if jsondata['result'] == "error":
        time.sleep(time_sleep)
        jsondata = json.loads(r.text)
        if jsondata['result'] == "error":
            time.sleep(time_sleep * 10)
            jsondata = json.loads(r.text)
    
    for contact in jsondata["data"]["contacts"]:
        contact = contact.get("contact", "")
        name = contact.get("name", "")
        position = contact.get("position", "")
        major = contact["user_pfmj"].get("mj_name1","")
        profession =  contact["user_pfmj"].get("pf_name1","")
        mmid = contact.get("mmid","")       

        sql = "SELECT COUNT(id) FROM maimai WHERE name LIKE '"+name+"' AND company LIKE '"+company+"';"
        cursor.execute(sql)
        if cursor._rows[0] != (0,):
            print(name + "\t\t\tskiped")
            continue

        sql = "INSERT INTO maimai(mmid, company, name, position, major, profession) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}')".format(mmid, company, name, position, major, profession)
        cursor.execute(sql)
        db.commit()
        print(name + "\t\t\tinserted")
        global insert_count
        insert_count += 1
        cursor.execute("UPDATE update_history SET result_count = {0} WHERE addId = {1};".format(insert_count, addId))
        cursor.fetchall()
        db.commit()




if __name__ == "__main__":
    writePID()
    logfile = open("crawler_log.txt", "w")
    print_method = "terminal"

    config = json.load(open("crawler_config.json"))


    print_method = config["DEFAULT"]['print_method']
    time_sleep = int(config['MAIMAI']['time_sleep'])
    time_out = int(config['DEFAULT']['time_out'])
    headers = config['MAIMAI']['headers']
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
    cursor.execute("INSERT INTO `update_histoy` (`addId`, `date`, `type`, `result_count`) VALUES ({0}, CURRENT_TIMESTAMP, 5, {1});".format(addId, insert_count))
    rows = cursor.fetchall()

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



    cursor.execute("SELECT company FROM company ORDER BY id DESC")
    rows = cursor.fetchall()
    for row in rows:
        try:
            print("____"+row[0]+"____")
            maimai(company=row[0], headers=headers, time_out=time_out)
            time.sleep(time_sleep)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            time.sleep(time_sleep)
            
