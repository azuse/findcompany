# !/usr/bin/python
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
from crawler_main_head import huazhan, baiduzhaopin, maimai
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
    def insert_company(self, huazhan_id="NULL", company="", address="", location="", tag="", homepage="", product="", regcapital="", contectName="", contectPosition="", contectPhone="", contectTel="", contectQq="", contectEmail="", contectAllJson="", exhibitionJson="", raw="", addId=0, description=""):
        if huazhan_id != "NULL":
            huazhan_id = "'{0}'".format(huazhan_id)
        sql = """INSERT INTO company (huazhan_id, company, tag, location, address, homePage, product, regCapital, contectName, contectPosition, contectPhone, contectTel, contectQq, contectEmail, contectAllJson, exhibitionJson, raw, addId, description) 
                    VALUES ({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}', {17}, '{18}')""" \
                    .format(huazhan_id, company, tag, location, address, homepage, product, regcapital, contectName, contectPosition, contectPhone, contectTel, contectQq, contectEmail, contectAllJson, exhibitionJson, raw, addId, description)
        self.db = pymysql.connect(host='localhost',
                                  user=self.user,
                                  passwd=self.password,
                                  db=self.database,
                                  charset='utf8')
        self.cursor = self.db.cursor()

        # self.cursor.execute(
        #     "SELECT COUNT(huazhan_id) FROM company WHERE huazhan_id LIKE '{0}';".format(id))
        # if self.cursor._rows[0] != (0,):
        #     print("info:  公司已存在")
        #     return -1

        # try:
        self.cursor.execute(sql)
        self.db.commit()
        self.db.close()
        return 0
        # except:
            
        self.db.close()
        return -1
    
    def is_company_exist(self, companyname):
        sql = "SELECT COUNT(*) FROM company WHERE company LIKE '{0}';".format(companyname)
        self.db = pymysql.connect(host='localhost',
                                  user=self.user,
                                  passwd=self.password,
                                  db=self.database,
                                  charset='utf8')
        self.cursor = self.db.cursor()
        self.cursor.execute(sql)
        self.db.close()

        if self.cursor._rows[0] != (0,):
            return True
        else:
            return False

    def insert_tag(self, keyword, ketword_weight, company, company_id):
        sql_check = "SELECT COUNT(keyword_id) count FROM company_keyword WHERE company_name LIKE '"+company+"' AND keyword LIKE '"+keyword+"';"
        self.db = pymysql.connect(host='localhost',
                                  user=self.user,
                                  passwd=self.password,
                                  db=self.database,
                                  charset='utf8')
        self.cursor = self.db.cursor()
        self.cursor.execute(sql_check)
        count = self.cursor.fetchall()
        if count[0][0] != 0:
            return -1

        sql_insert = "INSERT INTO company_keyword (company_id, company_name, keyword, keyword_weight) VALUES ('{0}','{1}','{2}','{3}');".format(company_id,company,keyword,ketword_weight)
        self.cursor.execute(sql_insert)
        self.db.commit()
        self.db.close()

        return 0

    def insert_baiduzhaopin(self, sid, name, company, city, depart, education, employertype, experience, label, jobclass, salary, location, url, companyaddress, companydescription, companysize, rowdata, company_id):
        sql = """INSERT INTO baiduzhaopin (sid, jobName, company, city, depart, education, employerType, experience, label, jobClass, salary, location, url, companyAddress, companyDescription, companySize, rowData, queryWord, companyId) VALUES
                                                                ('{0}', '{1}'  ,'{2}'   ,'{3}',  '{4}' , '{5}'    , '{6}'       , '{7}'     , '{8}', '{9}'   , '{10}', '{11}'  ,'{12}','{13}'        , '{14}'            , '{15}'     , '{16}' , '{17}'   ,'{18}');""" \
                                                        .format(sid, name, company, city, depart, education, employertype, experience, label, jobclass, salary, location, url, companyaddress, companydescription.replace("'", ""), companysize, rowdata, company, company_id)
        self.db = pymysql.connect(host='localhost',
                            user=self.user,
                            passwd=self.password,
                            db=self.database,
                            charset='utf8')
        self.cursor = self.db.cursor()                
        self.cursor.execute(
            "SELECT COUNT(sid) FROM baiduzhaopin WHERE sid LIKE '{0}';".format(sid))
        if self.cursor._rows[0] != (0,):
            return -1

        self.cursor.execute(sql)
        self.db.commit()
        self.db.close()
        return 0

    def insert_maimai(self, mmid, name, position, major, profession, company):
        self.db = pymysql.connect(host='localhost',
                            user=self.user,
                            passwd=self.password,
                            db=self.database,
                            charset='utf8')
        self.cursor = self.db.cursor()   
        sql = "SELECT COUNT(id) FROM maimai WHERE name LIKE '"+name+"' AND company LIKE '"+company+"';"
        self.cursor.execute(sql)
        if self.cursor._rows[0] != (0,):
            return -2

        sql = "INSERT INTO maimai(mmid, company, name, position, major, profession) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}')".format(mmid, company, name, position, major, profession)
        self.cursor.execute(sql)
        self.db.commit()
        return 0

    def get_company_id_by_company(self, company):
        self.db = pymysql.connect(host='localhost',
                            user=self.user,
                            passwd=self.password,
                            db=self.database,
                            charset='utf8')
        self.cursor = self.db.cursor()   
        sql = "SELECT id FROM company WHERE company LIKE '"+company+"' ;"
        self.cursor.execute(sql)
        
        data = self.cursor.fetchall()
        return data[0][0]  
    


##########################################
# 调用结巴分词提取关键词                    #
# @param content 待分词的句子             #
# @return array 包含关键词，权重的二维数组  #
########################################
def jieba_tf_idf(content, topK = 10):
    
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


#################################################
# 使用百度搜索搜索公司主页                          #
# @param company 公司名称                        #
# @return companyUrl 公司主页链接（未找到时为""）   #
#################################################
def baidu_search_homepage(company):
    url = "http://www.baidu.com/s?wd="+company+"%20官网"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    ret = soup.select("div[class='f13'] > a")
    if len(ret) == 0:
        print(company + " not found")
        return ""
    if ret[0].text.find("\xa0") != -1:
        companyUrl = ret[0].text.split("\xa0")[0]     #百度搜索会在网页链接后加一个'\xa0'需要手动去掉
        return companyUrl
    else:
        return ""


# =========================
# | 抓取公司官网三层的链接    |
# | 错误返回空字符串         |
# =========================
def company_homepage_crawler(homepage):
    if homepage == None:
        return ""
    print("getting url " + homepage)
    if(homepage.find("http://") == -1 and homepage.find("https://") == -1):
        homepage = "http://{0}".format(homepage)
    text = ""
    try:
        r = requests.get(homepage, timeout=time_out, proxies=proxies)
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
            r_sec = requests.get(href, timeout=time_out, proxies=proxies)
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
        #         r_thd = requests.get(href, timeout = time_out, proxies=proxies)
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
    config = json.load(open(opt.config_path, encoding="utf8"))
    print_method = config["DEFAULT"]['print_method']
    time_out = int(config['DEFAULT']['time_out'])

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
    page_wanted = config['BAIDU']['page_wanted']

    # 百度搜索的延迟时间 建议设置到60以上
    time_sleep = int(config['BAIDU']['time_sleep'])
    print("info: baidu time sleep set to " + str(time_sleep))

    # 百度搜索使用的header cookie设置直接从浏览器中复制
    headers_baidu = config['BAIDU']['headers']

    # 初始化华展云搜索选项
    #######################################################################################################
    ## huazhan ##
    headers_huazhan = config['HUAZHAN']['headers']
    keywords_huazhan = config['HUAZHAN']['keywords']
    username_huazhan = config["HUAZHAN"]["username"]
    password_huazhan = config["HUAZHAN"]["password"]
    # 华展云的延迟时间
    time_sleep_huazhan = int(config['HUAZHAN']['time_sleep'])
    print("info: huazhan time sleep set to " + str(time_sleep_huazhan))
    # 华展云排序类型 1：综合排序 2：时间排序
    sort_type_huazhan = config['HUAZHAN']['sort_type']

    huazhan = huazhan(
                headers=headers_huazhan, 
                proxies=proxies,
                time_sleep=time_sleep_huazhan, 
                sort=sort_type_huazhan, 
                print_method=print_method, 
                logfileHandler=logfile, 
                time_out=time_out,
                username=username_huazhan,
                password=password_huazhan
                )

    #######################################################################################################
    time_sleep_maimai = config['MAIMAI']['time_sleep']
    username_maimai = config["MAIMAI"]["username"]
    password_maimai = config["MAIMAI"]["password"]

    maimai = maimai(
                    time_sleep=time_sleep_maimai,
                    time_out=time_out,
                    print_method=print_method,
                    proxies=proxies,
                    username=username_maimai,
                    password=password_maimai
                    )

    print("-----------start crawling-----------")
    
    tmpdb = pymysql.connect(host='localhost',
                            user=db_username,
                            passwd=db_password,
                            db=db_dbname,
                            charset='utf8')
    tmpcursor = tmpdb.cursor()

    tmpcursor.execute("SELECT MAX(addId) FROM update_history; ")
    rows = tmpcursor.fetchall()
    if(rows[0][0] == None):
        addId = 1
    else:
        addId = rows[0][0] + 1

    insert_count = 0
    tmpcursor.execute("INSERT INTO `update_history` (`addId`, `date`, `type`, `result_count`) VALUES ({0}, CURRENT_TIMESTAMP, 1, {1});".format(addId, insert_count))
    rows = tmpcursor.fetchall()
    tmpdb.commit()

    baiduzhaopin = baiduzhaopin(   
                                headers=headers_baidu, 
                                proxies=proxies,
                                time_sleep=time_sleep,
                                logfileHandler=logfile,
                                print_method=print_method,
                                time_out=time_out
                                )

    inserted = 0
    insert_part_log = open("log/insert_part.log","w")

    for keyword in keywords:
        for keycity in keycities:
            print(keycity)
            print(keyword)
            page = 0
            while page < page_wanted:

                rows_baiduzhaopin = baiduzhaopin.baiduzhaopin(query=keyword, city=keycity, pn=page)
                if(rows_baiduzhaopin == -1):
                    break
                page += 1
                for row_baiduzhaopin in rows_baiduzhaopin:
                    # company maimai homepage hireinfo tag
                    insert_part = [0,0,0,0,0]

                    huazhan_id = ""
                    company = row_baiduzhaopin['company']
                    if company.find("某") != -1:
                        print("info: company filtered: {0}".format(company))
                        continue
                    if db.is_company_exist(company):
                        print("info: company exist: {0}".format(company))
                        continue
                    print("info: starting to insert company: {0}".format(company))
                    description = row_baiduzhaopin.get("companydescription", "")
                    tag = ""
                    location = row_baiduzhaopin.get("city", "")
                    address = ""
                    homePage = ""
                    product = ""
                    regCapital = ""
                    contectName = ""
                    contectPosition = ""
                    contectPhone = ""
                    contectTel = ""
                    contectQq = ""
                    contectEmail = ""
                    contectAllJson = ""
                    exhibitionJson = ""
                    raw = ""
                    addId = addId
                    id = 0

                    rows_huazhan = huazhan.huazhan_search_company_list(keyword=company, page=0)
                    for row_huazhan in rows_huazhan:
                        if(re.sub(r"<.*?>", "", row_huazhan["names"]) == company):
                            print("info: huazhan imformation matched")
                            rdata_huazhan = huazhan.huazhan_search_company_detail(row_huazhan['id'])
                            rdata_detail = rdata_huazhan['detail']
                            rdata_contects = rdata_huazhan['cur']
                            rdata_exhibitions = rdata_huazhan['pro']
                            
                            huazhan_id = rdata_detail.get("id","")
                            tag = rdata_detail.get('trades',"")
                            address = rdata_detail.get("address","")
                            homePage = rdata_detail.get("url", "")
                            product = rdata_detail.get("product","")
                            regCapital = rdata_detail.get("regcapital","")

                            if rdata_contects != None:
                                contect_main = huazhan.find_main_contect(rdata_contects)
                            else:
                                contect_main = dict()

                            contectName = contect_main.get("name","")
                            contectPosition = contect_main.get("position","")
                            contectPhone = contect_main.get("phone","")
                            contectTel = contect_main.get("tel","")
                            contectQq = contect_main.get("qq","")
                            contectEmail = contect_main.get("email","")
                            
                            contectAllJson = json.dumps(rdata_contects)
                            exhibitionJson = json.dumps(rdata_exhibitions)

                            raw = json.dumps(row_huazhan)

                            
                            
                            break
                    if huazhan_id == "":
                        print("info: huazhan information no match")

                    ret = db.insert_company(
                                            huazhan_id=huazhan_id,
                                            company=company,
                                            description=description,
                                            address=address,
                                            location=location,
                                            tag=tag,
                                            homepage=homePage,
                                            product=product,
                                            regcapital=regCapital,
                                            contectName=contectName,
                                            contectPosition=contectPosition,
                                            contectPhone=contectPhone,
                                            contectTel=contectTel,
                                            contectQq=contectQq,
                                            contectEmail=contectEmail,
                                            contectAllJson=contectAllJson,
                                            exhibitionJson=exhibitionJson,
                                            raw=raw,
                                            addId=addId
                                        )
                    if ret == 0:
                        print("info: company inserted: {0}".format(company))
                        id = db.get_company_id_by_company(company)
                        insert_count += 1
                        tmpcursor.execute("UPDATE update_history SET result_count = {0} WHERE addId = {1};".format(insert_count, addId))
                        tmpcursor.fetchall()
                        tmpdb.commit()
                        insert_part[0] = 1
                    else:
                        print("info: sql insert fail in company insert")
                        print("Unexpected error:", sys.exc_info()[0])


                    
                    ret = maimai.maimai(company)
                    for contact in ret:
                        contact = contact.get("contact", "")
                        maimai_name = contact.get("name", "")
                        maimai_position = contact.get("position", "")
                        maimai_major = contact["user_pfmj"].get("mj_name1","")
                        maimai_profession =  contact["user_pfmj"].get("pf_name1","")
                        maimai_mmid = contact.get("mmid","")       

                        ret = db.insert_maimai(maimai_mmid, maimai_name, maimai_position, maimai_major, maimai_profession, company)
                        if(ret == 0):
                            print("info: maimai inserted {0} {1} {2}".format(maimai_name, maimai_position, company))
                            insert_part[1] = 1
                        elif (ret == -2):
                            print("info: maimai existed {0} {1}".format(maimai_name, company))
                        else:
                            print("error: maimai insert fail")
                            print("Unexpected error:", sys.exc_info()[0])
                    if( insert_part[1] == 0):
                        print("info: maimai not found")


                    if homePage == "":
                        homePage = baidu_search_homepage(company)
                    if homePage != "":
                        print("info: homepage found: {0}".format(homePage))
                        homePage_text = company_homepage_crawler(homePage)
                        if homePage_text != "":
                            tags = jieba_tf_idf(homePage_text)
                            for tag in tags:
                                db.insert_tag(tag[0], tag[1], company, id)
                            print("info: tags for homepage inserted")
                            insert_part[2] = 1
                    else:
                        print("info: homepage not found")


                    # 查找该公司的招聘信息
                    hireinfo = baiduzhaopin.baiduzhaopin(company, location)
                    if hireinfo != -1:
                        for row in hireinfo:
                            try:
                                # 百度百聘id
                                sid = row.get('@sid', "")
                                # 招聘的职位名字
                                name = row.get("@name", "")
                                # 所在城市
                                city = row.get("city", "")
                                # 所在部门
                                depart = row.get("depart", "")
                                # 要求教育水平
                                education = row.get("education", "")
                                # 雇主种类
                                employertype = row.get("employertype", "")
                                # 经验
                                experience = row.get("experience", "")
                                # 标签
                                first_level_label = row.get("first_level_label", "")
                                second_level_label = row.get("second_level_label", "")
                                third_level_label = row.get("third_level_label", "")

                                label = first_level_label + ',' + second_level_label + ',' + third_level_label
                                # 工作种类
                                jobfirstclass = row.get("jobfirstclass", "")
                                jobsecondclass = row.get("jobsecondclass", "")
                                jobthirdclass = row.get("jobthirdclass", "")

                                jobclass = jobfirstclass + ',' + jobsecondclass + ',' + jobthirdclass
                                # 月薪
                                salary = row.get("salary", "")
                                # 地点
                                location = row.get("location", "")
                                # 详细链接
                                url = row.get("pc_url", "")
                                # 公司地址 公司介绍 公司规模 公司id
                                companyaddress = row.get("companyaddress", "")
                                companydescription = row.get("companydescription", "")
                                companysize = row.get("companysize", "")
                                company_id = row.get("company_id", "")
                                # 生数据
                                rowdata = json.dumps(row)

                                ret = db.insert_baiduzhaopin(
                                                            sid=sid,
                                                            name=name,
                                                            company=company,
                                                            city=city,
                                                            depart=depart,
                                                            education=education,
                                                            employertype=employertype,
                                                            experience=experience,
                                                            label=label,
                                                            jobclass=jobclass,
                                                            salary=salary,
                                                            location=location,
                                                            url=url,
                                                            companyaddress=companyaddress,
                                                            company_id=company_id,
                                                            companydescription=companydescription,
                                                            companysize=companysize,
                                                            rowdata=rowdata
                                                            )
                                if ret == 0:
                                    print("info: hireinfo inserted {0}".format(name))
                                    insert_part[3]=1
                                else:
                                    print("info:  sql insert fail in hireinfo insert")
                                    print("Unexpected error:", sys.exc_info()[0])

                                tags = jieba_tf_idf(name, topK=5)
                                for tag in tags:
                                    db.insert_tag(tag[0], tag[1], company, id)
                                print("info: tags for hireinfo inserted")
                            except:
                                print("error:  error in retreiving hiring info")
                                print("Unexpected error:", sys.exc_info()[0])
                    tags = jieba_tf_idf(description, topK=10)
                    for tag in tags:
                        db.insert_tag(tag[0], tag[1], company, id)
                    insert_part[4] = 1
                    print("info: tags for company description inserted")
                    insert_part_string = ' '.join(str(e) for e in insert_part)
                    insert_part_log.write("{0} {1}".format(insert_part_string, company))
                    print("info: one company insert program finished, continuing...")
                    print("")

                                
                                


            
                        
