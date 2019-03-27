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
    if ret != -1:
        for row in ret:
            try:
                sid = row.get('@sid', "")

                name = row.get("@name", "")
                city = row.get("city", "")

                depart = row.get("depart", "")

                education = row.get("education", "")
                employertype = row.get("employertype", "")
                experience = row.get("experience", "")

                first_level_label = row.get("first_level_label", "")
                second_level_label = row.get("second_level_label", "")
                third_level_label = row.get("third_level_label", "")

                label = first_level_label + ',' + second_level_label + ',' + third_level_label

                jobfirstclass = row.get("jobfirstclass", "")
                jobsecondclass = row.get("jobsecondclass", "")
                jobthirdclass = row.get("jobthirdclass", "")

                jobclass = jobfirstclass + ',' + jobsecondclass + ',' + jobthirdclass

                salary = row.get("salary", "")

                location = row.get("location", "")

                url = row.get("pc_url", "")

                companyaddress = row.get("companyaddress", "")
                companydescription = row.get("companydescription", "")
                companysize = row.get("companysize", "")
                company_id = row.get("company_id", "")

                rowdata = json.dumps(row)
                sql = """INSERT INTO baiduzhaopin (sid, jobName, company, city, depart, education, employerType, experience, label, jobClass, salary, location, url, companyAddress, companyDescription, companySize, rowData, queryWord, companyId) VALUES
                                                ('{0}', '{1}'  ,'{2}'   ,'{3}',  '{4}' , '{5}'    , '{6}'       , '{7}'     , '{8}', '{9}'   , '{10}', '{11}'  ,'{12}','{13}'        , '{14}'            , '{15}'     , '{16}' , '{17}'   ,'{18}');""" \
                                        .format(sid, name, company, city, depart, education, employertype, experience, label, jobclass, salary, location, url, companyaddress, companydescription.replace("'", ""), companysize, rowdata, company, company_id)
                
                cursor.execute(
                    "SELECT COUNT(sid) FROM baiduzhaopin WHERE sid LIKE '{0}';".format(sid))
                if cursor._rows[0] != (0,):
                    continue

                cursor.execute(sql)
                db.commit()
                print("____" + name + " ____已插入")
            except:
                print("Unexpected error:", sys.exc_info()[0])

            