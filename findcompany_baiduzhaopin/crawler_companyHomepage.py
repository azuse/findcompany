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

time_sleep = 10

import crawler_mysql
## 3个功能
## - 融合华展云和百度百聘
## - 从百度找官网
## - 从企名片找官网

### 从企名片抓取官网
def get_homepage_from_qimingpian(companyName):
    


### 将华展云的公司主页和百度百聘的公司主页表融合
def merge_huazhanyun_Homepages_with_baiduzhaopin_Homepages():
    sql = "SELECT MAX(id) FROM huazhan_company;"
