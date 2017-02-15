import socket
import math
import random 

UDP_IP = "192.168.16.195"
UDP_PORT = 5005
MESSAGE = "50,50,"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(0,1000):
	#angle = math.radians((i % 360 - 180))
	angle = math.radians((random.uniform(44, 50)))
	msg = MESSAGE + "{:0.2f}".format(angle)
	sock.sendto(msg, (UDP_IP, UDP_PORT))
	print msg
	