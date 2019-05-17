#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from __future__ import print_function
from collections import OrderedDict
import time
import psutil
import os.path
import re
import tornado.auth
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import unicodedata
import json
import urllib
import pymongo
from decimal import Decimal
import time,datetime
import os
import redis

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", home),
            (r"/getchaininfo", getchaininfo),
            (r"/gethashes", gethashes),
            (r"/getblocks", getblocks),
            (r"/getpooltransactions", getpooltransactions),
            (r"/gettxstatus", gettxstatus),
            (r"/newblock", newblock),
            (r"/newtransaction", newtransaction),
            # (r"/lpush", lpush),
        ]
        settings = dict(
            xsrf_cookies=False,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
    @property
    # @tornado.gen.coroutine
    def redisd(self):
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379,password='pass')
        redisd = redis.Redis(connection_pool=pool)
        return redisd

    # string
    @tornado.gen.coroutine
    def get(self,key):
        raise tornado.gen.Return(self.redisd.get(key))

    @tornado.gen.coroutine
    def set(self,key,value):
        raise tornado.gen.Return(self.redisd.set(key,value))
    # hash
    @tornado.gen.coroutine
    def hget(self,key,field):
        raise tornado.gen.Return(self.redisd.hget(key,field))
    @tornado.gen.coroutine
    def hmset(self, key, value):
        raise tornado.gen.Return(self.redisd.hmset(key,value))
    @tornado.gen.coroutine
    def hgetall(self, key):
        raise tornado.gen.Return(self.redisd.hgetall(key))
    # list
    @tornado.gen.coroutine
    def lpush(self, key, value):
        raise tornado.gen.Return(self.redisd.lpush(key, value))
    @tornado.gen.coroutine
    def zrange(self,key,start,end):
        raise tornado.gen.Return(self.redisd.zrange(key,start,end))

    # zset
    @tornado.gen.coroutine
    def zrangebyscore(self,key,start,end,withscores,offset,count):
        if withscores:
            raise tornado.gen.Return(self.redisd.zrangebyscore(key,start,end,"withscores",offset,count))
        else:
            raise tornado.gen.Return(self.redisd.zrangebyscore(key,start,end,offset,count))
            pass

class home(BaseHandler):
    def get(self):
        self.write("TAUT Main Net Test")

class getchaininfo(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        try:
            data = yield tornado.gen.Task(self.hgetall, "chaininfo")
        except Exception as e:
            print ("Get Chain Info, Redis Error: ", e)
        payload = {
        "message":"chaininfo",
        "payload":data
        }

        self.finish(json.dumps(payload))

class gethashes(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        try:
            jsondata = json.loads(self.request.body)
            startno= jsondata['startno']
            amount= jsondata['amount']
            reverse= jsondata['reverse']
        except Exception as e:
            print(e)

        print(startno, amount, reverse)

        # Get Current Block Height
        blockCurrent = yield tornado.gen.Task(self.hget,"chaininfo","totalheight")

        if reverse:
            blockStartNo = max(0, int(startno) - int(amount)+ 1)
            blockEndNo = min(int(blockCurrent), int(startno))
        else:
            blockStartNo = max(0, int(startno))
            blockEndNo = min(int(startno) + int(amount)- 1, int(blockCurrent))

        print(blockStartNo, blockEndNo)
        hashData = yield tornado.gen.Task(self.zrange,"blockhashinfo",str(blockStartNo),str(blockEndNo))
        print(hashData)
        amountBack= blockEndNo- blockStartNo+ 1
        data={
            "startno":blockStartNo,
            "amount":amountBack,
            "reverse":False,
            "hashes":hashData,
        }

        payload = {
        "message":"hashes",
        "payload":data
        }
        self.finish(json.dumps(payload))

class getblocks(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        try:
            jsondata = json.loads(self.request.body)
            startno= jsondata['startno']
            amount= jsondata['amount']
            reverse= jsondata['reverse']
        except Exception as e:
            print(e)
        print(startno, amount, reverse)

        # Get Current Block Height
        blockCurrent = yield tornado.gen.Task(self.hget,"chaininfo","totalheight")

        if reverse:
            blockStartNo = max(0, int(startno) - int(amount)+ 1)
            blockEndNo = min(int(blockCurrent), int(startno))
        else:
            blockStartNo = max(0, int(startno))
            blockEndNo = min(int(startno) + int(amount)- 1, int(blockCurrent))

        blockData = yield tornado.gen.Task(self.zrange,"blockinfo",str(blockStartNo),str(blockEndNo))

        amountBack= blockEndNo- blockStartNo+ 1

        data={
            "startno":blockStartNo,
            "amount":amountBack,
            "reverse":False,
            "blocks":blockData,
        }

        payload = {
            "message":"blocks",
            "payload":data
        }

        self.finish(json.dumps(payload))

class getpooltransactions(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        try:
            jsondata = json.loads(self.request.body)
            amount= jsondata['amount']
            minfee= jsondata['minfee']
        except Exception as e:
            print(e)

        print(minfee, amount)

        txids = yield tornado.gen.Task(self.zrangebyscore, "transfeepool",str(minfee),"+inf",False,0,amount)
        txs=[]
        for txid in txids:
            txTmp=""
            txTmp=yield tornado.gen.Task(self.hget, "transtxidpool",str(txid))
            # "transtxidpool"
            txs.append(txTmp)

        data={
            "minfee":minfee,
            "txs":txs
        }

        payload = {
            "message":"pooltransactions",
            "payload":data
        }

        self.write(json.dumps(payload))

class gettxstatus(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        name = yield tornado.gen.Task(self.get, "name")
        self.write(json.dumps({"name":name}))

# class lpush(BaseHandler):
#     @tornado.gen.coroutine
#     def post(self):
#         name = yield tornado.gen.Task(self.lpush,"nbqueue","newBlockData")
#         self.finish()
#         # self.finish(str(name))
#         pass
class newblock(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        jsondata = json.loads(self.request.body.decode('utf-8'))
        print(jsondata,"\n")
        clientHeight= int(jsondata["number"])
        clientHash= jsondata["previoushash"]
        clientDifficulty= int(jsondata["totaldifficulty"], 16)

        currentState = yield tornado.gen.Task(self.hgetall, "chaininfo")
        currentHeight= int(currentState["totalheight"])+ 1
        currentHash= currentState["currenthash"]
        currentDifficulty= int(currentState["totaldifficulty"], 16)

        print (clientHeight, clientHash, clientDifficulty)
        print (currentState, currentHeight, currentDifficulty,"\n")

        # Contrast to server state: 1. block height; 2. previous block hash; 3. total difficulty
        if ((currentHeight== clientHeight) and (currentHash == clientHash) and (currentDifficulty< clientDifficulty)):
            # This triggle is used for new block processing.
            newBlockData= clientHash+ "_"+ jsondata["block"]
            print (newBlockData)
            name = yield tornado.gen.Task(self.lpush,"nbqueue",newBlockData)
        self.finish()

class newtransaction(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        print(self.request)
        jsondata = json.loads(self.request.body.decode('utf-8'))
        try:
            print("Transaction is: \n",jsondata["transaction"])
            name = yield tornado.gen.Task(self.lpush,"transqueue",jsondata["transaction"])
        except Exception as e:
            print ("New Transaction Error: ", e)
        self.finish()

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(4000)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
