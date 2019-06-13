#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib
from urllib import parse
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
import configparser
import os
import pprint
import jieba.analyse
import jieba

# =========================
# | 验证url是否合法          |
# =========================
regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validateURL(url):
    if(re.match(regex, url) is None):
        return False
    else:
        return True











class baiduzhaopin:
    def __init__(self, headers, proxies, time_sleep, logfileHandler, print_method, time_out=20):
        self.time_sleep = time_sleep
        self.headers = headers
        self.proxies = proxies
        self.logfile = logfileHandler
        self.print_method = print_method
        self.time_out = time_out
    
    def print(self, text, text2=""):
        if self.print_method == "terminal":
            sys.stdout.write(str(text))
            sys.stdout.write(str(text2))
            sys.stdout.write("\n")
        else:
            self.logfile.write(str(text))
            self.logfile.write(str(text2))
            self.logfile.write("\n")
            self.logfile.flush()

    # =========================
    # | 获取百度百聘页面中的token |
    # =========================
    def getToken(self, query, city):
        time_sleep = self.time_sleep
        headers = self.headers
        proxies = self.proxies

        self.print("info: 获取token")
        url = "https://zhaopin.baidu.com/quanzhi?query=" + \
            parse.quote(query)+"&city="+parse.quote(city)
        
        while 1:
            try:
                r = requests.get(url, headers=headers, timeout=self.time_out, proxies=proxies, allow_redirects=True)
                self.print("info:get token sucess, sleep")
                time.sleep(time_sleep)

                break
            except:
                self.print("error: 获取token时网络错误,重试")
                self.print("Unexpected error:", sys.exc_info()[0])
                
                time.sleep(time_sleep)

                continue
        index = r.text.index('data["nekot"] = "')
        token = r.text[index+17:index+17+44]
        # reverse token
        token = token[::-1]
        token = parse.quote(token)
        url = "http://zhaopin.baidu.com/api/news?type=5&token="+token
        try:
            r = requests.get(url, proxies=proxies)
            time.sleep(time_sleep)

        except:
            pass
        self.print("info: new token:"+token)
        return token

    # =========================
    # | 查询职位详细信息函数      |
    # | loc     职位返回的loc   |
    # =========================
    def baiduzhaopin_detail(self, loc):
        time_sleep = self.time_sleep
        headers = self.headers
        proxies = self.proxies

        detailurl = "http://zhaopin.baidu.com/szzw?id="+loc
        if(validateURL(detailurl)):
            try:
                r = requests.get(detailurl, proxies=proxies, timeout=self.time_out)
                soup = BeautifulSoup(r.text, features="html.parser")
                return soup.select(".job-detail")[0].get_text()
            except ConnectionError as err:
                self.print("ConnectionError: '{0}'".format(err))
                return ""
            except:
                self.print("Unexpected error:", sys.exc_info()[0])
                return ""
        else:
            return ""

                

    # =========================
    # | 百度招聘api查询函数      |
    # | 查询职位列表            |
    # | query   查询关键词      |
    # | city     所在城市       |
    # | pn     开始页数         |
    # =========================
    def baiduzhaopin(self, query, city, pn = 0):
        time_sleep = self.time_sleep
        headers = self.headers
        proxies = self.proxies

        # rn意义不明 也许是每次返回的结果数？
        rn = 10
        # pn返回第pn个开始的结果 pn/10相当于 页
        
        token = self.getToken(query, city)
        # #####IMPORTANT#####
        # token 必须要有 不让强制搜索"招聘",但是token的值无所谓
        # api后台有校验,校验过程不清楚,校验失败query会强制变成"招聘"
        # 即使token设置正确，抓取数据的频率过高也会被ban，ban的应该是ip

        url = "http://zhaopin.baidu.com/api/qzasync?query=" + parse.quote(query) + "&city=" + parse.quote(
            city) + "&is_adq=1&pcmod=1&token=" + token + "&pn=" + str(pn) + "&rn=" + str(rn) + "&sort_type=1&sort_key=5"


        try:
            r = requests.get(url, proxies=proxies, headers=headers, timeout=self.time_out)
            self.print("info: get baidubaipin data sucess, sleep")
            time.sleep(time_sleep)
        except:            
            self.print("error: request timeout")
            return -1
             
        r.encoding = 'utf8'
        rdata = json.loads(r.text)
        if rdata['data'].get('errno', "") == -1 or rdata['data']['disp_data'] == None:
            self.print("info: 数据获取失败,可能是已经取得了所有结果")
            return -1

        hilight = rdata['data']['hilight'].split("\x00")[0]
        if hilight != query:
            self.print("error: token失效,或抓取受到限制")
            token = self.getToken(query, city)
            return -1


        return rdata['data']['disp_data']















class huazhan:
    areaid = {
        '北京':"e3EbEKiJ",
        '上海':"eTKbTKiz",
        '广东':"e8EcAEz6",
        '陕西':"e8bEEEmJ",
        '香港':"eww8AEzN",
        '海南':"eTAT8Ei6",
        '湖北':"ecKw8EiN",
        '辽宁':"eKdKEEmz",
        '安徽':"ebwwEEmN",
        '吉林':"eKETKEm6"
    }

    def __init__(self, headers, proxies, time_sleep, sort, logfileHandler, print_method, time_out=20, username="", password=""):
        self.time_sleep = time_sleep
        self.headers = headers
        self.proxies = proxies
        self.sort = sort
        self.username = username
        self.password = password
        self.huazhan_login()
        self.logfile = logfileHandler
        self.print_method = print_method
        self.time_out = time_out

    def print(self, text, text2=""):
        if self.print_method == "terminal":
            sys.stdout.write(str(text))
            sys.stdout.write(str(text2))
            sys.stdout.write("\n")
        else:
            self.logfile.write(str(text))
            self.logfile.write(str(text2))
            self.logfile.write("\n")
            self.logfile.flush()

    ## 找出最合适的联系人 ##
    ## 经理 重要度 +2
    ## 手机 重要度 +1
    ## 法人 重要度 -1 
    def find_main_contect(self, contects):
        for item in contects:
            item['priority'] = 0

        for item in contects:
            position = item.get("position", "")
            if position == "" or position.find("法人") != -1:
                item["priority"] -= 1
            if position.find("经理") != -1:
                item['priority'] += 1


        for item in contects:
            phone = item.get('phone', "")
            if phone != "":
                item['priority'] += 1
             
        max_priority = contects[0]['priority']
        max_priority_contect = 0
        i = 0
        while i < len(contects):
            if contects[i]['priority'] > max_priority:
                max_priority = contects[i]['priority']
                max_priority_contect = i
            i += 1

        return contects[max_priority_contect]

    def huazhan_search_company_detail(self, id):
        headers = self.headers
        proxies = self.proxies
        time_sleep = self.time_sleep

        url = "http://yun.ihuazhan.net/Index/eDetail"
        data = {
            "id":   id,
            "state":	2,
            "requestType":	"searchEnterprise"
        }

        try:
            r = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=self.time_out)
            time.sleep(time_sleep)
        except ConnectionError as err:
            self.print("ConnectionError: '{0}'".format(err))
            return -1
        except:
            self.print("Unexpected error:", sys.exc_info()[0])
            return -1


        r.encoding = 'utf-8'
        rdata = json.loads(r.text)

        return rdata


    def huazhan_search_company_list(self, keyword, page):
        headers = self.headers
        proxies = self.proxies
        time_sleep = self.time_sleep
        sort = self.sort

        url = "http://yun.ihuazhan.net/Index/enterpriseAjax"
        headers["Referer"] = "http://yun.ihuazhan.net/Index/enterprise?type=1&keyword=" + parse.quote(keyword)
        data = {
            "keyword":	keyword,
            "tradeid":	"",
            "areaid":	"",
            "companys":	10,
            "sort":	sort,
            ## islink=1 限定有联系方式的公司 ##
            "islink":	1,
            ## isurl=1 由企业网址的公司
            "isurl":	1,
            "istrack":	0,
            "special":	0,
            "type":	1,
            "pagecode":	page
        }

        try:
            r = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=self.time_out)
            
            time.sleep(time_sleep)
        except ConnectionError as err:
            self.print("ConnectionError: '{0}'".format(err))
            return -1
        except:
            self.print("Unexpected error:", sys.exc_info()[0])
            return -1

        r.encoding = 'utf-8'
        if r.status_code == 403:
            self.print("error: site return 403")
            return -1
        # self.print(r.text)
        try:
            rdata = json.loads(r.text)
        except:
            return -1 

        if not rdata["data"]:
            return -1
        return rdata["data"]

    def huazhan_login(self):
        headers = self.headers
        proxies = self.proxies
        time_sleep = self.time_sleep

        url = "http://yun.ihuazhan.net/Login/loginCheck"
        data = {
            "userName": self.username,
            "password": self.password
        }
        r = requests.post(url, data=data, headers=headers, proxies=proxies)
        # self.print(r.text)








class maimai:
    def __init__(self, time_sleep=30, time_out=20,print_method="terminal", proxies = {"http": None, "https": None}, username="", password=""):
        self.time_sleep = time_sleep
        self.time_out = time_out
        self.print_method = print_method
        self.proxies = proxies
        self.session = requests.session()
        self.session.post(
            url="https://acc.maimai.cn/login",
            data =  {
                "m": username,
                "p": password
            }
        )


    def print(self, text, text2=""):
        if self.print_method == "terminal":
            sys.stdout.write(str(text))
            sys.stdout.write(str(text2))
            sys.stdout.write("\n")
        else:
            self.logfile.write(str(text))
            self.logfile.write(str(text2))
            self.logfile.write("\n")
            self.logfile.flush()


    def maimai(self, company):
        time_sleep = self.time_sleep
        time_out = self.time_out
        proxies = self.proxies

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

        r = self.session.get(url=url, params=data, proxies=proxies, timeout=time_out)
        jsondata = json.loads(r.text)
        if jsondata['result'] == "error":
            time.sleep(time_sleep)
            jsondata = json.loads(r.text)
            if jsondata['result'] == "error":
                time.sleep(time_sleep * 10)
                jsondata = json.loads(r.text)
        
        return jsondata["data"]["contacts"]