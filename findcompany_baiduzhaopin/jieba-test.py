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

# from django.utils.http import urlquote


class mysql_union:

    def __init__(self, user, password, database):
        self.db = pymysql.connect(host='localhost',
                                  user=user,
                                  passwd=password,
                                  db=database,
                                  charset='utf8')
        self.cursor = self.db.cursor()


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

sql = "SELECT id,company FROM baiduzhaopin;"

cursor.execute(sql)

data = cursor.fetchall()
for item in data:
    id = item[0]
    company = item[1]
    print("-----------"+item[1]+"-----------")

    tag = jieba_tf_idf(company)
    print("-----------"+tag+"-----------")
    print("")
    
    sql = "UPDATE baiduzhaopin SET `tf-idf`='"+tag+"' WHERE id="+str(id)+" ;"
    cursor.execute(sql)
    db.commit()
    
