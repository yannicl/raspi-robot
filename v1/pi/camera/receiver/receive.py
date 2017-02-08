import socket
import time
import datetime

UDP_IP = "192.168.16.195"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
	data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
	print datetime.datetime.now().isoformat() + " : ", data