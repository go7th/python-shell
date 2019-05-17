#!/usr/bin/env python
import os,socket,time,sys

def check_port():
	port = [4000]

	while(1):
		for _each_port in port:
			#listen port
			try:
				sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sk.settimeout(2)
				sk.connect(('localhost',_each_port))
				sk.close
				#print "port success"
			except socket.error:
				#print "port error, restart"
				command= ' python /root/monitoring.py 1>>/root/monitoring.log 2>>/root/monitoring.err&'
				os.system(command)
				print "4000 port restart, check it"
		time.sleep(5.0)

if __name__ == '__main__':
  check_port()
