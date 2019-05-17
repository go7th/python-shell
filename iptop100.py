import time
import os
import re

DATE = time.strftime("%Y%m%d", time.localtime())
LOG_PATH = '/usr/local/nginx/logs/'

def get_top_100Ip():
    ps  = os.popen("awk '{print $1}' /usr/local/nginx/logs/access.log20190414 |sort | uniq -c |sort -n -k 1 -r | head -n 10")
    processes = []
    f=ps.readlines()
    rank100 = []
    for v in f:
        numall = ""
        numall = v.strip().split(' ')[0]
        ip = ""
        ip = v.strip().split(' ')[1]
        urlps = ""
        # urlps = os.popen(" awk '{print $1,$7}' /usr/local/nginx/logs/access.log20190409 | grep "+str(ip)+"| sort -n -k 2| uniq -c  ")
        urlps = os.popen(" awk '{print $1,$7}' /usr/local/nginx/logs/access.log20190414 | grep "+str(ip)+" |sort |uniq -c | sort -n -r -k 1")
        urlf = ""
        urlf = urlps.readlines()
        # print(urlf)
        rankline={
            "numall":numall,
            "ip":ip,
            "urls":[]
        }
        for urlres in urlf:
            print(urlres)
            num = ""
            num = urlres.strip().split(' ')[0]
            url = ""
            url = urlres.strip().split(' ')[1]
            ipurl = ""
            ipurl = urlres.strip().split(' ')[2]
            urls={
                "num":num,
                "url":ipurl
            }
            rankline["urls"].append(urls)
            # print(url,ipurl)
            pass
        rank100.append(rankline)
    return rank100

if __name__ == "__main__":
    #print(get_top_100())
    #data = get_detail()
    # get_detail()
    rank100 = get_top_100Ip()
    print(rank100)
    #get_data()
