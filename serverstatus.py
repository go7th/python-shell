import commands
import os
import json
import requests
import pymysql
import time
import datetime
import time


class serverstatus(object):

    def get_cpu_percent(self,ip):
        response = requests.post("http://"+ip+"/get_cpu_info")
        cpu_percent = json.loads(response.text)["cpu_percent"]
        return cpu_percent

    def get_mem_percent(self,ip):
        response = requests.post("http://"+ip+"/get_mem_info")
        info = json.loads(response.text)
        mem_percent = info["percent"]
        disk_percent = round((float(info["used"])/float(info["total"]))*100,1)
        return {
            "mem_percent":mem_percent,
            "disk_percent":disk_percent,
        }



    def connect_db(self):
        db = pymysql.connect("ip", "user", "pass", 'db')
        return db

    def insertsql(self, objdata):
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql='insert into serverstatus (num,cpu,mem,disk,time) values ("'+str(objdata['index'])+'","'+str(objdata['cpu'])+'","'+str(objdata['mem'])+'","'+str(objdata['disk'])+'","'+str(time)+'")'
        db = self.connect_db()
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as error:
            db.rollback()
            print(error)


if __name__ == "__main__":

    serverstatus = serverstatus()

    ips = [

    ]

    for i, ip in enumerate(ips):

        obj = {}
        cpu = serverstatus.get_cpu_percent(ip)
        data = serverstatus.get_mem_percent(ip)
        obj = {
            "index": i+1,
             "cpu": cpu,
             "mem": data["mem_percent"],
             "disk": data["disk_percent"],
        }
        serverstatus.insertsql(obj)
