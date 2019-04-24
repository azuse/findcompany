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
import traceback

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

jieba.load_userdict("dict.txt")
for item in data:
    id = item[0]
    company = item[1]
    url = item[2]
    seg_list = jieba.cut(company)  # 默认是精确模式
    print(", ".join(seg_list))
    input()
    