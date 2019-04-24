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


##########################################
# 调用结巴分词提取关键词                    #
# @param content 待分词的句子             #
# @return array 包含关键词，权重的二维数组  #
########################################
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

########## insert keyword from company name(tf-idf) 插入公司名称中的关键词 ########### 
sql = "SELECT id, company FROM company"
cursor.execute(sql)
data = cursor.fetchall()
jieba.load_userdict("dict.txt")

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

        

########## insert keyword from company description(tf-idf) 插入公司描述中的关键词 ###########
sql = "SELECT id,company,description FROM company"
cursor.execute(sql)
data = cursor.fetchall()

for item in data:
    id = item[0]
    company = item[1]
    description = item[2]

    if description == "" or description == None:
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


######### insert keyword from baiduzhaopin job description(tf-idf) 插入百度百聘中公司招聘的关键词 ###########
sql = "SELECT id,company FROM company"
cursor.execute(sql)
data = cursor.fetchall()

for item in data:
    id = item[0]
    company = item[1]
    sql = "SELECT jobName FROM baiduzhaopin WHERE company LIKE '{0}';".format(company)
    cursor.execute(sql)
    data2 = cursor.fetchall()
    print("-------"+company+"-------")

    for item2 in data2:
        jobName = item2[0]


        if jobName == "":
            continue
        

        tags = jieba_tf_idf(jobName)
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