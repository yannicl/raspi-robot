import socket
import thread
import time
import math

UDP_MY_IP = "192.168.16.195"
UDP_ROBOT_IP = "192.168.16.199"
COMMAND = "250,-250"
UDP_PORT = 5005

NBR_SAMPLES = 40
nbrPts = 0
isStart = True
samplesArray = []

def send_command_once():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(COMMAND, (UDP_ROBOT_IP, UDP_PORT))

# -------- UDP position listener -------
def listen_udp_and_send_command():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_MY_IP, UDP_PORT))
	global isStart, nbrPts, samplesArray
	
	while nbrPts < NBR_SAMPLES:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		values = data.split(',')
		sample_time = float(values[0]);
		theta = float(values[3]);
		nbrPts = nbrPts + 1
		if (isStart):
			isStart = False
			SAMPLES_START = sample_time
		
		samplesArray.append((sample_time - SAMPLES_START, theta))	
		
		send_command_once()

def processSamples(samples):
	for tuple in samples:
		print "{:0.4f}, {:0.4f}".format(tuple[0], tuple[1])
	
thread.start_new_thread(listen_udp_and_send_command, ())
time.sleep(4)
processSamples(samplesArray)
