from flask import Flask
from flask import request
from flask import render_template
import mysql.connector
import pprint
import json
import jieba.analyse
import jieba
import synonyms

app = Flask(__name__)
config = json.load(open("config.json",encoding="utf-8"))
db_password = config["mysql"]["password"]
db_username = config['mysql']['username']
db_dbname = config['mysql']['databasename']

def mysql_search(keyword, start, len, options):
    # start = 0
    # len = 20
    # keyword = ""
    # options = json.loads('{"hasContect":1,"hasAddress":1,"hasHomePage":1,"notLeagal":1,"inFavorite":1,"notFavorite":1,"sort":"timeDESC","shanghai":0,"beijing":true,"guangzhou":0,"shenzhen":0,"otherCities":0}')
    
    db = mysql.connector.connect(host='localhost',
                        user=db_username,
                        passwd=db_password,
                        db=db_dbname,
                        charset='utf8')
    cursor = db.cursor()

    if options['hasContect']:
        hasContect = 1
    else:
        hasContect = 0
    
    if options['hasAddress']:
        hasAddress = 1
    else:
        hasAddress = 0

    if options['hasHomePage']:
        hasHomePage = 1
    else:
        hasHomePage = 0

    if options['notLeagal']:
        notLeagal = 1
    else:
        notLeagal = 0
    
    if options['sort'] == 'timeDESC':
        sort = 'id'
        isasc = 0
    else:
        sort = 'id'
        isasc = 1

    isCompany = 1



    cursor.execute("call clear_cities()")
    if options['shanghai']:
        cursor.execute("call add_city('上海')")
    if options['beijing']:
        cursor.execute("call add_city('北京')")
    if options['guangzhou']:
        cursor.execute("call add_city('广州')")
    if options['shenzhen']:
        cursor.execute("call add_city('深圳')")
    if options['otherCities']:
        cursor.execute("call add_city('')")
    if not options['shanghai'] and not options['beijing'] and not options['guangzhou'] and not options['shenzhen'] and not options['otherCities']:
        cursor.execute("call add_city('')")
        
    sql = "call search_all('{0}',{1},{2},{3},{4},{5},{6},{7},{8},{9})".format(keyword, '0', isasc, hasContect, hasAddress, hasHomePage, notLeagal, isCompany, start, len)
    iterable = cursor.execute(sql, multi=True)
    result1 = False
    result2 = False
    for item in iterable:
        if(item.with_rows):
            if(not result1):
                result1 = item.fetchall()
            else:
                result2 = item.fetchall()
    if result2:
        return [result1,result2,sql]
    else:
        return [[],[[0]],sql]
    


@app.route('/api/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        start = request.form["start"]
        len = request.form["len"]
        keyword = request.form["keyword"]
        options = json.loads(request.form["options"])

        keyword_list = jieba.cut(keyword)
        good_keyword_list = []
        good_keyword_list.append(keyword)
        for word in keyword_list:
            good_keyword_list.append(word)
            synonyms_list = synonyms.nearby(word)
            for synonyms_word,synonyms_val in zip(synonyms_list[0],synonyms_list[1]):
                if(synonyms_val > 0.7):
                    good_keyword_list.append(synonyms_word)

        good_keyword_list = list(set(good_keyword_list))

        # debug = False
        # if debug:
        #     start = 0
        #     len = 20
        #     keyword = ""
        #     options = json.loads('{"hasContect":1,"hasAddress":1,"hasHomePage":1,"notLeagal":1,"inFavorite":1,"notFavorite":1,"sort":"timeDESC","shanghai":0,"beijing":true,"guangzhou":0,"shenzhen":0,"otherCities":0}')
        
        result1_list = []
        result2_count = 0
        sql_list = []
        # search every single keyword
        for good_keyword in good_keyword_list:
            ret = mysql_search(good_keyword, start, len, options)
            
            result1 = ret[0]
            result2 = ret[1]
            sql = ret[2]

            result1_list.extend(result1)
            result2_count += result2[0][0]
            sql_list.append(sql)

        result1_list = list(set(result1_list))

        dataBuf = {}
        dataBuf["mysqlquery"] = sql_list
        dataBuf['data'] = []
        i=0
        for row in result1_list:
            tmp = {}
            tmp['id'] = row[0]
            tmp['huazhan_id'] = row[1]
            tmp['company'] = row[2]
            tmp['description'] = row[3]
            tmp['tag'] = row[4]
            tmp['location'] = row[5]
            tmp['address'] = row[6]
            tmp['homePage'] = row[7]
            tmp['product'] = row[8]
            tmp['regCapital'] = row[9]
            tmp['contectName'] = row[10]
            tmp['contectPosition'] = row[11]
            tmp['contectPhone'] = row[12]
            tmp['contectTel'] = row[13]
            tmp['contectQq'] = row[14]
            tmp['contectEmail'] = row[15]
            tmp['contectAllJson'] = row[16]
            tmp['exhibitionJson'] = row[17]
            tmp['raw'] = row[18]
            tmp['favorite'] = row[18]
            tmp['addDate'] = row[19]
            dataBuf['data'].append(tmp)

        dataBuf["resultNumber"] = result2_count
        pprint.pprint(good_keyword_list)
        return json.dumps(dataBuf)
    
    else:
        error = "please use post method"
        return error
