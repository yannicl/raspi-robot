import socket
import thread
import time
import math

UDP_IP = "192.168.16.195"
UDP_PORT = 5005

sumRot = 0.0
isStart = True

# -------- UDP position listener -------
def listen_udp():
	UDP_IP = "192.168.16.195"
	UDP_PORT = 5005
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		values = data.split(',')
		theta = float(values[2]);
		global isStart, sumRot
		if (isStart):
			isStart = False
		else :
			if (theta < -1.57 and angleStart > 1.57):
				sumRot += (theta - angleStart) + 2.0 * math.pi
			elif (theta > 1.57 and angleStart < -1.57):
				sumRot += (theta - angleStart) - 2.0 * math.pi
			else:
				sumRot += (theta - angleStart)
		angleStart = theta

thread.start_new_thread(listen_udp, ())

time.sleep(10)
print math.degrees(sumRot)