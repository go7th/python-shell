# -*- coding: utf-8 -*-
import pymysql
import time
import re
import csv
# Addresses
fbList = []
with open('./newtest.csv') as fileRead:
    fbList= fileRead.readlines()


try:
   db = pymysql.connect("127.0.0.1", "user", "pass", "db")
   cursor = db.cursor()
except Exception as e:
   db = None
   print(str(e))

with open("newtest.csv","w") as csvfile:
    writer = csv.writer(csvfile)

    #先写入columns_name
    writer.writerow(["fb_id"])
    #写入多行用writerows
    writer.writerows([newfiledata])
    # break
