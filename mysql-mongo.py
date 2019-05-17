# -*- coding: utf-8 -*-
import pymysql
import pymongo
import time
import os
import json
import re

# abList = []
# fb_ids = []
# os.system("echo 'select fb_id,email from tauchain.accounts ' | mysql -utaumysql -pTaucoin@2018> fb_id.xls")
# with open('./fb_id.xls') as fileRead:
#     abList= fileRead.readlines()
# for addTemp in abList:
#     abTemp= addTemp.split(" ")
#     fb_ids.append(abTemp[0].strip())
try:
    client = pymongo.MongoClient('127.0.0.1', 27017)
    db=client.TAU
    db.authenticate("user", "pass")

except Exception as e:
   db = None
   print(str(e))
print(db)


try:
   mysqldb = pymysql.connect("ip", "user", "pass", "db")
   cursor = mysqldb.cursor()
except Exception as e:
   mysqldb = None
   print(str(e))

lengthnnn = 170000;
allemail = db.user.find({},{"email":1,"facebookId":1,"_id":0}).skip(lengthnnn)
allemailarr = list(allemail)
print(len(allemailarr))
emails = []
i=lengthnnn
for emailstr in allemailarr:
    i+=1
    # print(i)
    if i%1000==0:
        print(i)
        pass
    if emailstr.get("email"):
        coinsql = "sql"
        pass
        try:
            cursor.execute(coinsql)
            coins = cursor.fetchall()
        except Exception as e:
            print(str(e))
            print(i)
            pass
