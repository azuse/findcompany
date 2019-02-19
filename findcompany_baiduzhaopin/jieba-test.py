import re
from bs4 import BeautifulSoup
import string
import random
import time
import pymysql
import json
import requests
from urllib import parse
import urllib
from optparse import OptionParser
import jieba.analyse
import jieba
import sys
sys.path.append('../')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import *
import traceback
from bosonnlp import BosonNLP

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
PROXY = "http://child-prc.intel.com:913"

webdriver.DesiredCapabilities.CHROME['proxy'] = {
    "httpProxy":PROXY,
    "ftpProxy":PROXY,
    "sslProxy":PROXY,
    "noProxy":None,
    "proxyType":"MANUAL",
    "class":"org.openqa.selenium.Proxy",
    "autodetect":False
}
driver = webdriver.Chrome(chrome_options=chrome_options)




# from django.utils.http import urlquote


class mysql_union:
    def __init__(self, user, password, database):
        self.db = pymysql.connect(host='localhost',
                                  user=user,
                                  passwd=password,
                                  db=database,
                                  charset='utf8')
        self.cursor = self.db.cursor()

fo = open("tf_idf_test.csv", "w")

def jieba_tf_idf(content, company):
    topK = 20
    withWeight = True
    tags = jieba.analyse.extract_tags(
        content, topK=topK, withWeight=withWeight)

    if withWeight is True:
        for tag in tags:
            print("tag: %s\t\t weight: %f" % (tag[0], tag[1]))
            fo.write("%s,%s,%f \n" % (company, tag[0], tag[1]))
            fo.flush()
    else:
        print(",".join(tags))

    return tags[0][0]

# print(jieba_tf_idf("大津编物（无锡）有限公司"))
db_username = "root"
db_password = "misakaxindex"
db_dbname = "findcompany"

db = pymysql.connect(host='localhost',
                    user=db_username,
                    passwd=db_password,
                    db=db_dbname,
                    charset='utf8')
cursor = db.cursor()

sql = "SELECT id,company,homePage FROM company;"

cursor.execute(sql)

data = cursor.fetchall()

regex = re.compile(
r'^(?:http|ftp)s?://' # http:// or https://
r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
r'localhost|' #localhost...
r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
r'(?::\d+)?' # optional port
r'(?:/?|[/?]\S+)$', re.IGNORECASE)

nlp = BosonNLP('1aooLCxg.33225.eMAXko7EljEV')

for item in data:
    id = item[0]
    company = item[1]
    url = item[2]
    if(url == "None"):
        continue
    
    if(url.find("http://") == -1 and url.find("https://") == -1):
        url = "http://" + url

    if(re.match(regex, url) is None):
        continue 

    print("getting url " + url)

    #### using selenium ####

    # driver.get(url)
    # soup = BeautifulSoup(driver.page_source, features="html.parser")
    # text = soup.get_text()
    # btn = driver.find_element_by_css_selector("a")
    
    # print("page get daze: "+ text)
    # jieba_tf_idf(text)

    #### using request ####
    try:
        r = requests.get(url, timeout = 5)
        r.encoding = "utf-8"
    except:
        print("Unexpected error:", sys.exc_info()[0])

        continue
    soup = BeautifulSoup(r.text,  features="html.parser")
    tagArray = ["p", "h1", "h2", "h3", "h4",  "h5", "h6", "label", "a", "span"]
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
            r_sec = requests.get(href, timeout = 5)
            r_sec.encoding = "utf-8"
        except:
            print("Unexpected error:", sys.exc_info()[0])
            continue
        soup_sec = BeautifulSoup(r_sec.text, features="html.parser")
        for i in range(len(tagArray)):
            res = soup.find_all(tagArray[i])
            for j in range(len(res)):
                text += "," + res[j].get_text()

  

    print("page get daze: "+ text)
    if text != "" and r.status_code == 200:
        jieba_tf_idf(text, company)
        
