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

# 百度招聘mysql插入函数
class mysql_union:

    def __init__(self, user, password, database):
        self.db = pymysql.connect(host='localhost',
                                  user=user,
                                  passwd=password,
                                  db=database,
                                  charset='utf8')
        self.cursor = self.db.cursor()

    def insert_baidu(self, data, queryword):
        sid = data.get('@sid', "")

        name = data.get("@name", "")
        company = data.get("company", "")
        city = data.get("city", "")

        depart = data.get("depart", "")

        education = data.get("education", "")
        employertype = data.get("employertype", "")
        experience = data.get("experience", "")

        first_level_label = data.get("first_level_label", "")
        second_level_label = data.get("second_level_label", "")
        third_level_label = data.get("third_level_label", "")

        label = first_level_label + ',' + second_level_label + ',' + third_level_label

        jobfirstclass = data.get("jobfirstclass", "")
        jobsecondclass = data.get("jobsecondclass", "")
        jobthirdclass = data.get("jobthirdclass", "")

        jobclass = jobfirstclass + ',' + jobsecondclass + ',' + jobthirdclass

        salary = data.get("salary", "")

        location = data.get("location", "")

        url = data.get("pc_url", "")

        companyaddress = data.get("companyaddress", "")
        companydescription = data.get("companydescription", "")
        companysize = data.get("companysize", "")
        company_id = data.get("company_id", "")

        rowdata = json.dumps(data)
        sql = """INSERT INTO baiduzhaopin (sid, jobName, company, city, depart, education, employerType, experience, label, jobClass, salary, location, url, companyAddress, companyDescription, companySize, rowData, queryWord, companyId) VALUES
                                        ('{0}', '{1}'  ,'{2}'   ,'{3}',  '{4}' , '{5}'    , '{6}'       , '{7}'     , '{8}', '{9}'   , '{10}', '{11}'  ,'{12}','{13}'        , '{14}'            , '{15}'     , '{16}' , '{17}'   ,'{18}');""" \
                                 .format(sid, name, company, city, depart, education, employertype, experience, label, jobclass, salary, location, url, companyaddress, companydescription.replace("'", ""), companysize, rowdata, queryword, company_id)
        self.cursor.execute(
            "SELECT COUNT(sid) FROM baiduzhaopin WHERE sid LIKE '{0}';".format(sid))
        if self.cursor._rows[0] != (0,):
            return 0

        try:
            self.cursor.execute(sql)
            self.db.commit()
            return 1
        except:
            return 0

    # 将查到的company官网链接插入数据库
    def insertCompany_baidu(self, company, cid, url):
        sql = """INSERT INTO companyHomepage (cid, company, url) VALUES ('{0}', '{1}'  ,'{2}');""" .format(
            cid, company, url)
        self.cursor.execute(
            "SELECT COUNT(cid) FROM companyHomepage WHERE cid LIKE '{0}';".format(cid))
        if self.cursor._rows[0] != (0,):
            return 0

        try:
            self.cursor.execute(sql)
            self.db.commit()
            return 1
        except:
            return 0

    def insertCompany_huazhan(self, detail, contects, exhibitions, raw):
        id = detail.get('id', "")
        name = detail.get('name', "")
        tag = detail.get('trades', "")
        location = detail.get('areas', "")
        address = detail.get('address', "")
        url = detail.get('url', "")
        # 产品介绍 #
        product = detail.get('prodcut', "")
        # regcaptal 注册资本#
        regcapital = detail.get("regcapital","")

        # 正向搜索有手机号的联系人
        contect_main = find_main_contect(contects)
        
        contect_main_name = contect_main.get('name', "")
        contect_main_phone = contect_main.get('phone', "")
        contect_main_tel = contect_main.get('tel', "")
        contect_main_qq = contect_main.get('qq', "")
        contect_main_email = contect_main.get('email', "")
        contect_main_position = contect_main.get('position', "")

        contect_all_json = json.dumps(contects)
        exhibitions_json = json.dumps(exhibitions)

        sql = """INSERT INTO huazhan_company (huazhan_id, company, tag, location, address, homePage, product, regCapital, contectName, contectPosition, contectPhone, contectTel, contectQq, contectEmail, contectAllJson, exhibitionJson, raw) 
                    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}')""" \
                    .format(id, name, tag, location, address, url, product, regcapital, contect_main_name, contect_main_position, contect_main_phone, contect_main_tel, contect_main_qq, contect_main_email, contect_all_json, exhibitions_json, raw)
        self.cursor.execute(
            "SELECT COUNT(huazhan_id) FROM huazhan_company WHERE huazhan_id LIKE '{0}';".format(id))
        if self.cursor._rows[0] != (0,):
            return 0

        try:
            self.cursor.execute(sql)
            self.db.commit()
            return 1
        except:
            return 0