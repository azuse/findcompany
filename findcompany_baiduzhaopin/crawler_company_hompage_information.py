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
import jieba.analyse
import jieba

#################################################
# 使用百度搜索搜索公司主页                          #
# @param company 公司名称                        #
# @return companyUrl 公司主页链接（未找到时为""）   #
#################################################
def baidu_search_homepage(company):
    url = "http://www.baidu.com/s?wd="+company+"%20官网"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    ret = soup.select("div[class='f13'] > a")
    if len(ret) == 0:
        print(company + " not found")
        return ""
    if ret[0].text.find("\xa0") != -1:
        companyUrl = ret[0].text.split("\xa0")[0]     #百度搜索会在网页链接后加一个'\xa0'需要手动去掉
        return companyUrl
    else:
        return ""


##########################################
# 调用结巴分词提取关键词                    #
# @param content 待分词的句子             #
# @return array 包含关键词，权重的二维数组  #
########################################
def jieba_tf_idf(content):
    topK = 10
    withWeight = True
    tags = jieba.analyse.extract_tags(
        content, topK=topK, withWeight=withWeight)

    if withWeight is True:
        for tag in tags:
            print("tag: %s\t\t weight: %f" % (tag[0], tag[1]))
    else:
        print(",".join(tags))

    return tags

regex = re.compile(
r'^(?:http|ftp)s?://' # http:// or https://
r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
r'localhost|' #localhost...
r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
r'(?::\d+)?' # optional port
r'(?:/?|[/?]\S+)$', re.IGNORECASE)

tagArray = ["p", "h1", "h2", "h3", "h4",  "h5", "h6", "label"]


############################################
#  获取公司网页的关键词                       #
#  @param url 公司网页域名                  # 
#  @return array 包含关键词，权重的二维数组   #
##########################################
def get_company_tf_idf(url):
    print("getting url " + url)
    try:
        r = requests.get(url, timeout = time_out)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return -1
    if r.status_code != 200:
        return -1
    
    soup = BeautifulSoup(r.text,  features="html.parser")

    text = ""

    for i in range(len(tagArray)):
        res = soup.find_all(tagArray[i])
        for j in range(len(res)):
            text += "," +  res[j].get_text()
    
    a_all = soup.find_all("a")
    for k in range(len(a_all)):
        href = a_all[k].attrs.get('href', "")
        if(href.find("http://") == -1 and href.find("https://") == -1):
            href = url + href
        if(re.match(regex, href) is None):
            continue 

        print("getting href " + href)

        try:
            r_sec = requests.get(href, timeout = time_out)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            continue
        soup_sec = BeautifulSoup(r_sec.text, features="html.parser")
        tagArray = ["p", "h1", "h2", "h3", "h4",  "h5", "h6", "label"]
        for i in range(len(tagArray)):
            res = soup.find_all(tagArray[i])
            for j in range(len(res)):
                text += "," + res[j].get_text()

    return jieba_tf_idf(text)

if __name__ == "__main__":
    usage = "usage: python3 crawler_companyInformation.py to archieve company detail and product"
    parser = OptionParser()
    parser.add_option("-c","--config", help="select a config file", metavar="crawler_config.json", default="crawler_config.json", dest="config_path")
    (opt, args) = parser.parse_args()

    config = json.load(open(opt.config_path))
    time_out = config['DEFAULT']['time_out']

    db_username = config['MYSQL']['db_username']
    db_password = config['MYSQL']['db_password']
    db_dbname = config['MYSQL']['db_dbname']

    db = pymysql.connect(host='localhost',
                        user=db_username,
                        passwd=db_password,
                        db=db_dbname,
                        charset='utf8')
    cursor = db.cursor()

    sql = "SELECT id,company,homePage FROM company;"
    cursor.execute(sql)
    data = cursor.fetchall()
    for item in data:
        id = item[0]
        company = item[1]
        url = item[2]
        url_baidusearch = baidu_search_homepage(company)
        if url_baidusearch != "":
            url = url_baidusearch
        
        if(url == "None"):
            continue
        
        if(url.find("http://") == -1 and url.find("https://") == -1):
            url = "http://" + url

        if(re.match(regex, url) is None):
            continue 

        tags = get_company_tf_idf(url)

        ### 将tags插入数据库

        

        