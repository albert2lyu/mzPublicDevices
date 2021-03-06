#!/usr/bin/env python
# coding: utf-8
try:
	import twisted  
except ImportError:  
	print "This examples requires the Twisted framework. Download it from http://twistedmatrix.com"  
	raise SystemExit
from twisted.internet.protocol import Protocol, Factory,DatagramProtocol
from twisted.internet import reactor
from datetime import datetime
import threading
import time
import json
#udp客户端
class Helloer(DatagramProtocol):
	def __init__(self,mzcallback,addr,port):
		self.mzcallback=mzcallback
		self.addr=addr
		self.port=port
		self.isthre=True
	def startProtocol(self):
		self.transport.connect(self.addr, self.port)
		
		tkey = threading.Thread(target=self.startsend,args=[self.transport,])
		tkey.setDaemon(True)
		tkey.start()
	def startsend(self,transport):
		while self.isthre:
			try:
				self.mzcallback(transport=transport,udp=self)
			except:
				reactor.listenUDP(0, Helloer(self.mzcallback,self.addr,self.port))
				break
				# self.transport.connect("127.0.0.1", 9999)
	def datagramReceived(self, data, (host, port)):

		print "received %r from %s:%d" % (data, host, port)
	def connectionRefused(self):
		print "No one listening"



class TimerProtocol(Protocol):
	"""docstring for TimerProtocol"""
	def __init__(self):
		self.timeout = 20
		self.interval = 0
		self.name="";
	def connectionLost(self, reason):
		print self.name
		self.factory.mzcall(self.name,False)
		Protocol.connectionLost(self, reason)
		self.stop()
		print "locst connection:",reason
		self.factory.number_of_connections -= 1
		print "number_of_connections:",self.factory.number_of_connections
	def connectionMade(self):  
		#如果服务器连接数超过最大连接数，拒绝新链接建立  
		if self.factory.number_of_connections >= self.factory.max_connections:  
			self.transport.write('Too many connections, try again later')  
			self.transport.loseConnection()  
			return  
		print self.transport.client
		# print '\n'.join(['%s:%s' % item for item in self.transport.__dict__.items()]) 
		#总连接数+1  
		# self.factory.mzcall(self.transport)
		self.factory.number_of_connections += 1
		# self.start()  
		# self.timeout_deferred = reactor.callLater(self.timeout, self.transport.loseConnection) 
	def dataReceived(self, data):  
		#去除server收到client数据两端的空格  
		data = data.strip() 
		retdata=json.loads(data)
		self.name=retdata['name'] 
		print data
		self.factory.mzcall(data)
		#如果收到的是'start'命令  
		if data == 'start':  
			# start sending a date object that contains the current time  
			if not self.started:  
				self.start()  
		elif data == 'stop':  
			self.stop()  
		#每次执行完客户端请求后重置timeout，重新开始计算无操作时间。  
		# if self.timeout_deferred:  
		# 	self.timeout_deferred.cancel()  
		# 	self.timeout_deferred = reactor.callLater(TimerProtocol.timeout, self.transport.loseConnection)
	def start(self):  
		self.started = True  
		self.sendTime()  
	def stop(self):  
		self.started = False  
	def sendTime(self):  
		if self.started:  
			#往缓存流里写入信息，用编码器进行amf编码  
			# self.encoder.writeElement(datetime.now())  
			#返回给客户端编码后的信息  
			if self.factory.mzcall:
				sendmsg=self.factory.mzcall()
				if sendmsg:
					# print self.transport.client
					self.transport.write(sendmsg)
			#重置缓存流  
			# self.stream.truncate()  
			#每隔self.interval的时间再发送一次amf信息  
			# if self.timeout_deferred:  
			# 	self.timeout_deferred.cancel()  
			# 	self.timeout_deferred = reactor.callLater(TimerProtocol.timeout, self.transport.loseConnection)
			reactor.callLater(self.interval, self.sendTime)

class TimerFactory(Factory):  
	protocol = TimerProtocol  
	#最大链接数  
	max_connections = 1000  
	def __init__(self,mzcall=False):  
		self.number_of_connections = 0
		self.mzcall=mzcall
class Server(object):
	"""docstring for Server"""
	def __init__(self,config,mzcall=False,register=False):
		self.host=config("server","host")
		self.appPort=int(config("server","port"))
		self.mzcall=mzcall
		self.register=register
	def run(self):
		print "Running Socket AMF gateway on %s:%s" % (self.host, self.appPort)    
		# reactor.listenUDP(0, Helloer(self.mzcall))  
		reactor.listenTCP(int(self.appPort), TimerFactory(self.register), interface=self.host)
		reactor.run()
	def updto(self,addr,port):
		reactor.listenUDP(0, Helloer(self.mzcall,addr,int(port)))
if __name__ == '__main__':  
	#设置域名，端口。  
	host = 'localhost'  
	appPort = 8000
	print "Running Socket AMF gateway on %s:%s" % (host, appPort)    
	reactor.listenTCP(int(appPort), TimerFactory(), interface=host)  
	reactor.run()  