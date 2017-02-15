import socket
import thread
import time
import math

UDP_MY_IP = "192.168.16.195"
UDP_ROBOT_IP = "192.168.16.199"
COMMAND = "-250,250"
UDP_PORT = 5005

sumRot = 0.0
NBR_SAMPLES = 40
nbrPts = 0
deltat = 0
isStart = True
samplesArray = []

def send_command(duration):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	max_range = int(duration / 0.020)
	for i in range (max_range):
		sock.sendto(COMMAND, (UDP_ROBOT_IP, UDP_PORT))
		time.sleep(0.020)
def send_command_once():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(COMMAND, (UDP_ROBOT_IP, UDP_PORT))

# -------- UDP position listener -------
def listen_udp_and_send_command():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_MY_IP, UDP_PORT))
	global isStart, sumRot, nbrPts, samplesArray, deltat
	start = time.time()
	while nbrPts < NBR_SAMPLES:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		values = data.split(',')
		theta = float(values[2]);
		samplesArray.append(theta)
		nbrPts = nbrPts + 1
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
		
		send_command_once()
	deltat = time.time() - start


send_command(1.0)		
thread.start_new_thread(listen_udp_and_send_command, ())
time.sleep(4)

print "Angular velocity for command {} : {:0.4f} ({:d} samples on {:0.4f})".format(COMMAND, sumRot / deltat, nbrPts, deltat)
print samplesArray