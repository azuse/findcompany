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
from crawler_main_head import huazhan, baiduzhaopin, maimai
import os 

logfile = None
config = json.load(open("crawler_config.json"))
print_method = "terminal"
time_out = int(config['DEFAULT']['time_out'])

proxies = {"http": "http://child-prc.intel.com:913",
                "https": "http://child-prc.intel.com:913"}
# proxies = {"http": None, "https": None}

time_sleep = int(config['BAIDU']['time_sleep'])
headers_baidu = config['BAIDU']['headers']

bd = baiduzhaopin(headers=headers_baidu,
                    proxies=proxies, time_sleep=time_sleep, print_method=print_method, logfileHandler=logfile, time_out=time_out)

print("百度百聘搜索列表")
ret = bd.baiduzhaopin("计算机视觉","上海")
pprint.pprint(ret)

print("百度百聘详细信息")
ret = bd.baiduzhaopin_detail(ret[0]['loc'])
pprint.pprint(ret)



headers_huazhan = config['HUAZHAN']['headers']
time_sleep_huazhan = int(config['HUAZHAN']['time_sleep'])
sort_type_huazhan = config['HUAZHAN']['sort_type']

hz = huazhan(headers=headers_huazhan, proxies=proxies,
                time_sleep=time_sleep_huazhan, sort=sort_type_huazhan, print_method=print_method, logfileHandler=logfile, time_out=time_out)

