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
    pidfile = open("mainPID.txt", "w")
    pidfile.write(str(os.getpid()))
    pidfile.write("\n")
    pidfile.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    pidfile.flush()
    pidfile.close()

logfile = open("crawler_log.txt", "w")
def print(text, text2=""):
    if print_method == "terminal":
        sys.stdout.write(str(text))
        sys.stdout.write(str(text2))
        sys.stdout.write("\n")
    else:
        logfile.write(str(text))
        logfile.write(str(text2))
        logfile.write("\n")
        logfile.flush()

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
            print("info:  公司已存在")
            return 0

        try:
            self.cursor.execute(sql)
            self.db.commit()
            self.db.close()
            print("info:  插入成功")
            return 1
        except:
            print("info:  插入失败")
            print(sql)
            print("Unexpected error:", sys.exc_info()[0])
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

    print("page get : " + text)
    return text


if __name__ == "__main__":
    # 初始化远程执行配置 将pid写到文件
    writePID()
    # 设置print method == terminal : 打印到标准输出流, !=terminal : 打印到文件
    print_method = "terminal"


    # 初始化 parser（其实用处不大）
    usage = "usage: python3 crawler_main.py main script for crawl company "
    parser = OptionParser()
    parser.add_option("-p", "--proxy", help="select a proxy",
                      metavar="intel / socks5 / noproxy", default="", dest="proxy_select")
    parser.add_option("-c", "--config", help="select a config file",
                      metavar="crawler_config.json", default="crawler_config.json", dest="config_path")
    (opt, args) = parser.parse_args()


    # 读取config file
    print('info: using config file: ' + opt.config_path)
    config = json.load(open(opt.config_path))
    print_method = config["DEFAULT"]['print_method']

    ######## MYSQL #########
    # 使用config中的配置初始化数据库
    db_username = config['MYSQL']['db_username']
    db_password = config['MYSQL']['db_password']
    db_dbname = config['MYSQL']['db_dbname']

    db = db(db_username, db_password, db_dbname)

    # 如果config中设置了proxy，优先级大于-p参数
    opt.proxy_select = config['DEFAULT'].get("proxy", opt.proxy_select)
    # 根据proxy选择初始化proxy，在intel内部使用intel proxy，外部使用noproxy
    if(opt.proxy_select == "intel"):
        print("info: using intel proxy")
        proxies = {"http": "http://child-prc.intel.com:913",
                   "https": "http://child-prc.intel.com:913"}
    elif(opt.proxy_select == "noproxy"):
        print("info: using no proxy")
        proxies = {"http": None, "https": None}

    # 初始化百度搜索的一系列选项
    #######################################################################################################
    ## baidu ##
    # 搜索的关键词 与 城市
    keywords = config['BAIDU']['keywords']
    keycities = config['BAIDU']['keycities']

    # 百度搜索的延迟时间 建议设置到60以上
    time_sleep = int(config['BAIDU']['time_sleep'])
    print("info: baidu time sleep set to " + str(time_sleep))

    # 百度搜索使用的header cookie设置直接从浏览器中复制
    headers_baidu = config['BAIDU']['headers']

    # 百度百聘搜索类
    bd = baiduzhaopin(headers=headers_baidu,
                      proxies=proxies, time_sleep=time_sleep, print_method=print_method, logfileHandler=logfile)

    # 初始化华展云搜索选项
    #######################################################################################################
    ## huazhan ##
    headers_huazhan = config['HUAZHAN']['headers']
    keywords_huazhan = config['HUAZHAN']['keywords']
    # 华展云的延迟时间
    time_sleep_huazhan = int(config['HUAZHAN']['time_sleep'])
    print("info: huazhan time sleep set to " + str(time_sleep_huazhan))
    # 华展云排序类型 1：综合排序 2：时间排序
    sort_type_huazhan = config['HUAZHAN']['sort_type']

    hz = huazhan(headers=headers_huazhan, proxies=proxies,
                 time_sleep=time_sleep_huazhan, sort=sort_type_huazhan, print_method=print_method, logfileHandler=logfile)

    print("-----------start crawling-----------")

    for keyword in keywords:
        for keycity in keycities:
            print(keycity)
            print(keyword)
            while(True):
                pn = 0
                # 调用百度搜索
                ret = bd.baiduzhaopin(keyword, keycity, pn)

                # 百度搜索没有结果 继续搜索下一个城市
                if ret == -1:
                    break

                # pn + 10 循环继续搜索下一页
                pn += 10

                # 处理搜索结果
                for item in ret:
                    # 公司名称
                    company = item.get("company", "")
                    # 公司地址
                    companyaddress = item.get("companyaddress", "")
                    # 公司介绍
                    companydescription = item.get("companydescription", "")
                    # 公司所在城市
                    city = item.get("city", "")
                    
                    # 百度百聘搜索公司详细信息需要调用loc
                    # loc = item.get("loc", "")
                    # detail = bd.baiduzhaopin_detail(loc)

                    # 公司详情提取关键词
                    # searchKeywords = jieba_tf_idf(detail, topK=10)

                    # 使用百度搜索搜索公司官网
                    # homepage = baidu_search_homepage(company)
                    # if(homepage.find("http://") == -1 and homepage.find("https://") == -1):
                    #     homepage = "http://" + homepage

                    # 抓取公司官网信息 提取关键词
                    # text = company_homepage_crawler(homepage)
                    # searchKeywords.append(jieba_tf_idf(text, topK=20))

                    # 使用公司名在华展云搜索公司列表
                    ret2 = hz.huazhan_search_company_list(company, 1)
                    if ret2 == -1:
                        continue

                    # 处理华展云搜索结果
                    for item in ret2:
                        # 华展云搜索公司详细信息
                        ret3 = hz.huazhan_search_company_detail(item["id"])
                        # detail 公司详细信息
                        detail = ret3["detail"]
                        # cur 联系人信息
                        contects = ret3["cur"]
                        # pro 参展信息
                        exhibitions = ret3["pro"]
                        # 保存原始json数据
                        raw = json.dumps(ret3)
                        # 公司的华展云id
                        id = detail.get('id', "")
                        # 公司名称
                        name = detail.get('name', "")
                        print(name)
                        # 华展云与百度百聘公司名称不匹配 跳过
                        if name != company:
                            continue


                        tag = detail.get('trades', "")
                        location = detail.get('areas', "")
                        address = detail.get('address', "")
                        homepage = detail.get('url', "")

                        # 产品介绍 #
                        product = detail.get('prodcut', "")
                        # regcaptal 注册资本#
                        regcapital = detail.get("regcapital", "")

                        # 对联系人的一些处理 因为联系人个数不确定 数据库中为 一个主联系人-手机-固话-邮件-qq + 所有联系人的json数据存储
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

                        # 插入到数据库
                        db.insert_company(huazhan_id=id, company=name, address=address, location=location, tag=tag, homepage=homepage, product=product, regcapital=regcapital, contectName=contect_main_name, contectPosition=contect_main_position,
                                        contectPhone=contect_main_phone, contectTel=contect_main_tel, contectQq=contect_main_qq, contectEmail=contect_main_email, contectAllJson=contect_all_json, exhibitionJson=exhibitions_json, raw=raw)
