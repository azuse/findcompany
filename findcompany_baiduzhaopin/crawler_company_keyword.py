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
import traceback

db_username = "root"
db_password = "misakaxindex"
db_dbname = "findcompany"

db = pymysql.connect(host='localhost',
                    user=db_username,
                    passwd=db_password,
                    db=db_dbname,
                    charset='utf8')
cursor = db.cursor()

def jieba_tf_idf(content):
    topK = 20
    withWeight = True
    tags = jieba.analyse.extract_tags(
        content, topK=topK, withWeight=withWeight)

    if withWeight is True:
        for tag in tags:
            print("tag: %s\t\t weight: %f" % (tag[0], tag[1]))
    else:
        print(",".join(tags))

    return tags

########## insert keyword from company name(tf-idf) ###########
sql = "SELECT id, company FROM company"
cursor.execute(sql)
data = cursor.fetchall()

for item in data:
    id = item[0]
    company = item[1]
    print("-------"+company+"-------")
    tags = jieba_tf_idf(company)
    for tag in tags:
        keyword = tag[0]
        ketword_weight = tag[1]
        
        sql_check = "SELECT COUNT(keyword_id) count FROM company_keyword WHERE company_name LIKE '"+company+"' AND keyword LIKE '"+keyword+"';"
        cursor.execute(sql_check)
        count = cursor.fetchall()
        if count[0][0] != 0:
            continue

        sql_insert = "INSERT INTO company_keyword (company_id, company_name, keyword, keyword_weight) VALUES ('{0}','{1}','{2}','{3}');".format(id,company,keyword,ketword_weight)
        cursor.execute(sql_insert)
        db.commit()

        

########## insert keyword from company description(tf-idf) ###########
sql = "SELECT id,company,description FROM company"
cursor.execute(sql)
data = cursor.fetchall()

for item in data:
    id = item[0]
    company = item[1]
    description = item[2]

    if description == "":
        continue
    
    print("-------"+company+"-------")

    tags = jieba_tf_idf(description)
    for tag in tags:
        keyword = tag[0]
        ketword_weight = tag[1]
        
        sql_check = "SELECT COUNT(keyword_id) count FROM company_keyword WHERE company_name LIKE '"+company+"' AND keyword LIKE '"+keyword+"';"
        cursor.execute(sql_check)
        count = cursor.fetchall()
        if count[0][0] != 0:
            continue

        sql_insert = "INSERT INTO company_keyword (company_id, company_name, keyword, keyword_weight) VALUES ('{0}','{1}','{2}','{3}');".format(id,company,keyword,ketword_weight)
        cursor.execute(sql_insert)
        db.commit()


########## insert keyword from baiduzhaopin job description(tf-idf) ###########
