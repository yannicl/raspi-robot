import pygame
import serial
from tendo import singleton
import thread
import time
import socket

me = singleton.SingleInstance() # will sys.exit(-1) if another instance is running
	
pygame.init()
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Init serial
ser = serial.Serial('/dev/ttyUSB0', 57600)
ser.write("A,0,000,0,000,S")

# Robot wheel speed
DIRECTION_FORWARD = '1'
DIRECTION_BACKWARD = '0'
haltRobot=True
udpFrame=False

def createFrame(leftDirection, _leftWheelSpeed, rightDirection, _rightWheelSpeed):
	frame = "A," + leftDirection + "," + format(_leftWheelSpeed, '03') + "," + rightDirection + "," + format(_rightWheelSpeed, '03') + ",S"
	return frame
def leftForwardSpeed(y):
	return y*237.5 + 17.5
def leftRot(x):
	return x*220
def rightForwardSpeed(y):
	return y*255
def rightRot(x):
	return x*(-255)
def combine(x,y,xvalue,yvalue):
	return int(abs(x)/(abs(x)+abs(y))*xvalue + abs(y)/(abs(x)+abs(y))*yvalue)
def rightSpeed(x,y):
	return combine(x,y,rightRot(x),rightForwardSpeed(y))
def leftSpeed(x,y):
	return combine(x,y,leftRot(x),leftForwardSpeed(y))
def createFrameSignedSpeeds(leftSpeed, rightSpeed):
	leftDir =  DIRECTION_FORWARD if (leftSpeed > 0) else DIRECTION_BACKWARD
	rightDir = DIRECTION_FORWARD if (rightSpeed > 0) else DIRECTION_BACKWARD
	return createFrame(leftDir, abs(leftSpeed), rightDir, abs(rightSpeed))

# ------- Command sender and logger ------
def send_frame(frame):
	UDP_CMD_LOGGER_IP = "192.168.16.195"
	UDP_CMD_LOGGER_PORT = 5005
	sock_cmd_logger = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock_cmd_logger.sendto(frame, (UDP_CMD_LOGGER_IP, UDP_CMD_LOGGER_PORT))
	if (not haltRobot):
		ser.write(frame)
	print frame
	
	
# -------- UDP command listener -------
def listen_udp():
	UDP_IP = "192.168.16.199"
	UDP_PORT = 5005
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	global udpFrame
	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		speeds = data.split(',')
		udpFrame=createFrameSignedSpeeds(int(speeds[0]), int(speeds[1]))

thread.start_new_thread(listen_udp, ())		

# -------- Main Program Loop -----------
while True:
	
	joystick = pygame.joystick.Joystick(0)
	
	# EVENT PROCESSING STEP
	for event in pygame.event.get(): # User did something
		
		# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
		if event.type == pygame.JOYBUTTONDOWN:		
			print("Joystick button pressed.")
			button0 = joystick.get_button(0)
			if (button0):
				haltRobot=True
				print "Robot stopped"
			button1 = joystick.get_button(1)
			if (button1):
				haltRobot=False
				print "Robot started"
			button2 = joystick.get_button(2)
			
			button3 = joystick.get_button(3)
			
		if event.type == pygame.JOYBUTTONUP:
			print("Joystick button released.")
	

	axis_x = joystick.get_axis(0)
	axis_y = -1*joystick.get_axis(1)
	if (abs(axis_x) > 0.125) or (abs(axis_y) > 0.125):
		frame = createFrameSignedSpeeds(leftSpeed(axis_x, axis_y),rightSpeed(axis_x, axis_y))
		send_frame(frame)
	elif (udpFrame):
		send_frame(udpFrame)
		udpFrame=False
		
	
	# Limit to 20 frames per second
	clock.tick(20)
	
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
