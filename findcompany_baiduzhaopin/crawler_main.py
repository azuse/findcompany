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
from crawler_main_head import huazhan, baiduzhaopin
import os 

def writePID():
    pidfile = open("mainPID.txt")
    pidfile.write(str(os.getpid))
    pidfile.flush()
    pidfile.close()


class db:
    def __init__(self, user, password, database):
        self.user = user
        self.password = password
        self.database = database

    # =========================
    # | 数据库插入函数           |
    # | 每一次插入开一个连接      |
    # | 防止脚本运行时数据库连接中断|
    # =========================
    def insert_company(self, huazhan_id="", company="", address="", location="", tag="", homepage="", product="", regcapital="", contectName="", contectPosition="", contectPhone="", contectTel="", contectQq="", contectEmail="", contectAllJson="", exhibitionJson="", raw=""):

        sql = """INSERT INTO company (huazhan_id, company, tag, location, address, homePage, product, regCapital, contectName, contectPosition, contectPhone, contectTel, contectQq, contectEmail, contectAllJson, exhibitionJson, raw) 
                    VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}')""" \
                    .format(huazhan_id, company, tag, location, address, homepage, product, regcapital, contectName, contectPosition, contectPhone, contectTel, contectQq, contectEmail, contectAllJson, exhibitionJson, raw)
        self.db = pymysql.connect(host='localhost',
                                  user=self.user,
                                  passwd=self.password,
                                  db=self.database,
                                  charset='utf8')
        self.cursor = self.db.cursor()

        self.cursor.execute(
            "SELECT COUNT(huazhan_id) FROM company WHERE huazhan_id LIKE '{0}';".format(id))
        if self.cursor._rows[0] != (0,):
            return 0

        try:
            self.cursor.execute(sql)
            self.db.commit()
            self.db.close()
            return 1
        except:
            self.db.close()
            return 0

# =========================
# | 调用结巴分词tf_idf       |
# =========================


def jieba_tf_idf(content, topK=20):

    withWeight = True
    tags = jieba.analyse.extract_tags(
        content, topK=topK, withWeight=withWeight)

    if withWeight is True:
        for tag in tags:
            print("tag: %s\t\t weight: %f" % (tag[0], tag[1]))
    else:
        print(",".join(tags))

    return tags


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

# =========================
# | 使用百度搜索搜索公司官网 |
# =========================


def baidu_search_homepage(company):
    url = "http://www.baidu.com/s?wd="+company+"%20官网"
    r = requests.get(url, proxies=proxies, timeout=5)
    soup = BeautifulSoup(r.text, features="html.parser")
    ret = soup.select("div[class='f13'] > a")
    if len(ret) == 0:
        print(company + " not found")
        return ""
    if ret[0].text.find("\xa0") != -1:
        companyUrl = ret[0].text.split("\xa0")[0]
        return companyUrl
    else:
        return ""

# =========================
# | 抓取公司官网三层的链接    |
# | 错误返回空字符串         |
# =========================


def company_homepage_crawler(homepage):
    print("getting url " + homepage)
    text = ""
    try:
        r = requests.get(homepage, timeout=5, proxies=proxies)
        r.encoding = "utf-8"
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return text

    soup = BeautifulSoup(r.text,  features="html.parser")
    tagArray = ["p", "h1", "h2", "h3", "h4",  "h5", "h6", "label", "a", "span"]
    for i in range(len(tagArray)):
        res = soup.find_all(tagArray[i])
        for j in range(len(res)):
            text += "," + res[j].get_text()

    a_all = soup.find_all("a")
    for k in range(len(a_all)):
        href = a_all[k].attrs.get('href', "")
        if(href.find("http://") == -1 and href.find("https://") == -1):
            href = homepage + href
        if(re.match(regex, href) is None):
            continue
        print("getting href " + href)

        try:
            r_sec = requests.get(href, timeout=5, proxies=proxies)
            r_sec.encoding = "utf-8"
        except:
            print("Unexpected error in sec:", sys.exc_info()[0])
            continue

        soup_sec = BeautifulSoup(r_sec.text, features="html.parser")
        for i in range(len(tagArray)):
            res = soup_sec.find_all(tagArray[i])
            for j in range(len(res)):
                text += "," + res[j].get_text()
    # 不搜索第三层 太多了
        # a_sec_all = soup_sec.find_all("a")
        # for p in range(len(a_sec_all)):
        #     href = a_sec_all[p].get("href", "")
        #     if(href.find("http://") == -1 and href.find("https://") == -1):
        #         href = homepage + href
        #     if(re.match(regex, href) is None):
        #         continue
        #     print("getting href " + href)

        #     try:
        #         r_thd = requests.get(href, timeout = 5, proxies=proxies)
        #         r_thd.encoding = "utf-8"
        #     except:
        #         print("Unexpected error in sec:", sys.exc_info()[0])
        #         continue

        #     soup_thd = BeautifulSoup(r_sec.text, features="html.parser")
        #     for i in range(len(tagArray)):
        #         res = soup_thd.find_all(tagArray[i])
        #         for j in range(len(res)):
        #             text += "," + res[j].get_text()

    print("page get daze: " + text)
    return text


if __name__ == "__main__":
    writePID()
    usage = "usage: python3 crawler_main.py main script for crawl company "
    parser = OptionParser()
    parser.add_option("-p", "--proxy", help="select a proxy",
                      metavar="intel / socks5 / noproxy", default="", dest="proxy_select")
    parser.add_option("-c", "--config", help="select a config file",
                      metavar="crawler_config.json", default="crawler_config.json", dest="config_path")
    (opt, args) = parser.parse_args()

    print('info: using config file: ' + opt.config_path)
    config = json.load(open(opt.config_path))
    ######## MYSQL #########
    db_username = config['MYSQL']['db_username']
    db_password = config['MYSQL']['db_password']
    db_dbname = config['MYSQL']['db_dbname']

    db = db(db_username, db_password, db_dbname)

    opt.proxy_select = config['DEFAULT'].get("proxy", opt.proxy_select)

    if(opt.proxy_select == "intel"):
        print("info: using intel proxy")
        proxies = {"http": "http://child-prc.intel.com:913",
                   "https": "http://child-prc.intel.com:913"}
    elif(opt.proxy_select == "socks5"):
        print("info: using socks5 proxy")
        proxies = {"http": "socks5://127.0.0.1:1080",
                   "https": "socks5://127.0.0.1:1080"}
    elif(opt.proxy_select == "noproxy"):
        print("info: using no proxy")
        proxies = {"http": None, "https": None}
    #######################################################################################################
    ## baidu ##
    keywords = config['BAIDU']['keywords']
    keycities = config['BAIDU']['keycities']
    time_sleep = int(config['BAIDU']['time_sleep'])
    print("info: baidu time sleep set to " + str(time_sleep))

    row_wanted = int(config['BAIDU']['row_wanted'])

    headers_baidu = config['BAIDU']['headers']

    bd = baiduzhaopin(headers=headers_baidu,
                      proxies=proxies, time_sleep=time_sleep)

    #######################################################################################################
    ## huazhan ##
    headers_huazhan = config['HUAZHAN']['headers']
    keywords_huazhan = config['HUAZHAN']['keywords']
    time_sleep_huazhan = int(config['HUAZHAN']['time_sleep'])
    print("info: huazhan time sleep set to " + str(time_sleep_huazhan))
    page_start_huazhan = int(config['HUAZHAN']['page_start'])
    page_end_huazhan = int(config['HUAZHAN']['page_end'])
    sort_type_huazhan = config['HUAZHAN']['sort_type']

    hz = huazhan(headers=headers_huazhan, proxies=proxies,
                 time_sleep=time_sleep_huazhan, sort=sort_type_huazhan)

    print("-----------start crawling-----------")

    for keyword in keywords:
        for keycity in keycities:
            print(keycity)
            print(keyword)
            pn = 0
            ret = bd.baiduzhaopin(keyword, keycity, pn)
            pn += 10
            if ret == -1:
                continue

            for item in ret:
                company = item.get("company", "")
                companyaddress = item.get("companyaddress", "")
                companydescription = item.get("companydescription", "")
                city = item.get("city", "")
                loc = item.get("loc", "")
                detail = bd.baiduzhaopin_detail(loc)
                searchKeywords = jieba_tf_idf(detail, topK=10)

                # homepage = baidu_search_homepage(company)
                # if(homepage.find("http://") == -1 and homepage.find("https://") == -1):
                #     homepage = "http://" + homepage

                # text = company_homepage_crawler(homepage)
                # searchKeywords.append(jieba_tf_idf(text, topK=20))

                ret2 = hz.huazhan_search_company_list(company, 1)
                if ret2 == -1:
                    continue
                for item in ret2:
                    ret3 = hz.huazhan_search_company_detail(item["id"])
                    detail = ret3["detail"]
                    contects = ret3["cur"]
                    exhibitions = ret3["pro"]
                    raw = ret3.text

                    id = detail.get('id', "")
                    name = detail.get('name', "")
                    tag = detail.get('trades', "")
                    location = detail.get('areas', "")
                    address = detail.get('address', "")
                    url = detail.get('url', "")

                    # 产品介绍 #
                    product = detail.get('prodcut', "")
                    # regcaptal 注册资本#
                    regcapital = detail.get("regcapital", "")

                    # 正向搜索有手机号的联系人
                    if contects != None:
                        contect_main = hz.find_main_contect(contects)
                    else:
                        contect_main = dict()

                    contect_main_name = contect_main.get('name', "")
                    contect_main_phone = contect_main.get('phone', "")
                    contect_main_tel = contect_main.get('tel', "")
                    contect_main_qq = contect_main.get('qq', "")
                    contect_main_email = contect_main.get('email', "")
                    contect_main_position = contect_main.get('position', "")

                    contect_all_json = json.dumps(contects)
                    exhibitions_json = json.dumps(exhibitions)

                    db.insert_company(huazhan_id=id, company=name, address=address, location=location, tag=tag, homepage=homepage, product=product, regcapital=regcapital, contectName=contect_main_name, contectPosition=contect_main_position,
                                      contectPhone=contect_main_phone, contectTel=contect_main_tel, contectQq=contect_main_qq, contectEmail=contect_main_email, contectAllJson=contect_all_json, exhibitionJson=exhibitions_json, raw=raw)
