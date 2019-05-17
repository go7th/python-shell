#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import gevent
from gevent import monkey
monkey.patch_all()

class ServerListen(object):

    def __init__(self):
        self.sleeptime=60.0 #循环时间
        self.issend=False  #默认没有宕机
        self.looplevel=0
        #状态0每个周期内都会邮件通知,发生宕机就会调整为状态1
        #状态1每60个周期内邮件通知,宕机恢复完成会自动调整为状态0
        self.loopstatus=0 #用于60个周期计数
        self.statusres=[] #协程请求返回的结果集
        self.html=""      #邮件发送的内容
        self.data=[
        {"ip":"172.31.23.91:4000","name":"rpc1"},
        {"ip":"172.31.31.138:4000","name":"rpc2"},
        ]
        #用于监控的rpc
        # self.receivers = ['809504937@qq.com'] # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        self.receivers = ['809504937@qq.com',"cheetah0801@126.com","clanthunder@qq.com"] # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        #用于通知管理员的邮箱
        self.sender = 'imorpheus@taucoin.io'
        #发送者的邮箱
    def sendemail(self,html,isdown):
        message = MIMEText(html,'plain','utf-8')
        if isdown:
            message['From'] = Header("服务器宕机", 'utf-8')   # 发送者
            message['To'] =  Header("服务器宕机", 'utf-8')        # 接收者
            subject = '服务器发生异常'
            pass
        else:
            message['From'] = Header("服务器已恢复正常", 'utf-8')   # 发送者
            message['To'] =  Header("服务器已恢复正常", 'utf-8')        # 接收者
            subject = '服务器已恢复正常'
            pass
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtp = smtplib.SMTP_SSL("172.31.18.86",port="465")
            smtp.login("imorpheus", "im123456")
            smtp.sendmail(self.sender, self.receivers, message.as_string())
            smtp.quit()
            # smtpObj = smtplib.SMTP('localhost')
            # smtpObj.sendmail(self.sender, self.receivers, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException as e :
            print("Error: 无法发送邮件")
            print(str(e))
    def sendemailactive(self,html):
        message = MIMEText(html,'plain','utf-8')
        message['From'] = Header("服务器宕机", 'utf-8')   # 发送者
        message['To'] =  Header("服务器宕机", 'utf-8')        # 接收者
        subject = '服务器发生异常'
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtp = smtplib.SMTP_SSL("172.31.18.86",port="465")
            smtp.login("imorpheus", "im123456")
            smtp.sendmail(self.sender, self.receivers, message.as_string())
            smtp.quit()
            # smtpObj = smtplib.SMTP('localhost')
            # smtpObj.sendmail(self.sender, self.receivers, message.as_string())
            print("邮件发送成功")
        except smtplib.SMTPException as e :
            print("Error: 无法发送邮件")
            print(str(e))

    def getrpc(self,ip,value):
        #一个异步函数请求接口
        url = "http://"+ip+"/active"
        try:
            resp = requests.post(url, data={})
            if resp.status_code == 200:
                self.statusres.append({"ip":ip,"name":value,"info":str(resp.text)})
        except Exception as e:
            self.statusres.append({"ip":ip,"name":value,"info":"down"})
            print(str(e))

    def run(self,data):
        self.statusres=[]
        lines = []
        for val in data:
            lines.append(gevent.spawn(tx.getrpc(val.get("ip"),val.get("name"))))
            pass
        gevent.joinall(lines)
        # print(self.statusres)


if __name__ == "__main__":
    tx = ServerListen()
    while 1:
        tx.html=""
        tx.issend=False
        tx.run(tx.data)
        for status in tx.statusres:
            tx.html+="\
            ip:"+str(status.get("ip"))+"\n\
            name:"+str(status.get("name"))+"\n\
            info:"+str(status.get("info"))+"\n\n\n"
            if status.get("info")=="down":
                tx.issend=True
                pass
        # tx.sendemail(tx.html)
        # print(tx.html)
        print(tx.issend)
        if tx.issend:
            if tx.looplevel==0:
                print(str(tx.loopstatus)+"---当前有服务器宕机,具体错误信息查看邮箱------"+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                tx.sendemail(tx.html,True)
                tx.looplevel+=1
            elif tx.looplevel==1:
                if tx.loopstatus==480:
                    tx.sendemail(tx.html,True)
                    tx.loopstatus=0
                else:
                    tx.loopstatus+=1
        else:
            print(str(tx.loopstatus)+"---当前正常------"+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
            if tx.looplevel==1:
                tx.looplevel=0
                tx.html+="当前已恢复正常---------"+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                tx.sendemail(tx.html,False)
                pass
            else:
                pass
        time.sleep(tx.sleeptime)
        pass
