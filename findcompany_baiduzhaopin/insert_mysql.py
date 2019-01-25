#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pymysql
import json

# mysql connection here: hostname, username, password, database name
db = pymysql.connect(host='localhost',
                       user='root',
                       passwd='misakaxindex',
                       db='findcompany',
                       charset='utf8')
cursor = db.cursor()
json_data=open("Archive 19-01-24 13-52-39.har").read()
data = json.loads(json_data)
for item in data["postList"]:
    postId = item['postId']
    name = item['name']
    publishDate=item['publishDate']
    postType=item['postType']
    workPlace=item["workPlace"]
    try:
        workYears=item["workYears"]
    except:
        workYears=""

    try:
        recruitNum=item["recruitNum"]
    except:
        recruitNum=""
    
    try:
        education = item['education']
    except:
        education=""
    
    try:
        serviceCondition = item['serviceCondition'].replace('\r','')
    except:
        serviceCondition = ""
    
    try:
        workContent = item['workContent'].replace('\r','')
    except:
        workContent = ""
    
    try:
        orgName = item['orgName']
    except:
        orgName = ""


    sql = u"INSERT INTO baiduzhaopin(postId, name, publishDate, workPlace, workYears, recruitNum, education, serviceCondition, workContent, orgName, postType) VALUES({0},'{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}'); ".format(postId, name, publishDate, workPlace, workYears, recruitNum, education, serviceCondition, workContent, orgName, postType)
    cursor.execute(sql)
    db.commit()
    
    