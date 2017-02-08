import cv2
import io
import time
import threading
import picamera
import math
import numpy as np;

# IMAGE PROCESSING ROUTINE

# Setup SimpleBlobDetector parameters.
def createSimpleBlobDetectorParams():
	params = cv2.SimpleBlobDetector_Params()

	params.filterByColor = False
	params.blobColor = 255;

	# Change thresholds
	params.minThreshold = 100;
	params.maxThreshold = 256;
	 
	# Filter by Area.
	params.filterByArea = True
	params.minArea = 9
	 
	# Filter by Circularity
	params.filterByCircularity = True
	params.minCircularity = 0.5
	 
	# Filter by Convexity
	params.filterByConvexity = False
	params.minConvexity = 0.5
	 
	# Filter by Inertia
	params.filterByInertia = False
	params.minInertiaRatio = 0.5
	
	return params



def exploreAroundKeypointAndComputeMean(keypoint, img):
	mean = np.multiply(img[0,0], 0.0)
	#print mean
	radius = int(keypoint.size)
	#print radius
	keyptx = int(keypoint.pt[0]+1)
	#print keyptx
	keypty = int(keypoint.pt[1]+1)
	#print keypty
	n = 1
	for x in xrange(keyptx - radius, keyptx + radius):
		for y in xrange(keypty - radius, keypty + radius):
			if (x >= 0 and x < 200 and y > 0 and y < 200):
				mean = np.add(mean, img[y, x])
				n = n + 1
	return np.divide(mean, n)
	
def distance(mean, color):
	return np.linalg.norm(mean-color)

def processKeypoints(keypoints, img, refPt):
	distances = [];
	for keypoint in keypoints:
		mean = exploreAroundKeypointAndComputeMean(keypoint, img);
		distances.append([distance(mean, [255,0,0]), distance(mean, [0,0,255])])
	if (len(distances) >= 2) :
		prob_1st_red = distances[0][0] / (distances[0][0] + distances[1][0]) - distances[0][1] / (distances[0][1] + distances[1][1])
		unwrappedPt1 = unwrap(keypoints[0].pt, refPt)
		unwrappedPt2 = unwrap(keypoints[1].pt, refPt)
		if (prob_1st_red > 0):
			redx = unwrappedPt1[0]
			redy = unwrappedPt1[1]
			bluex = unwrappedPt2[0]
			bluey = unwrappedPt2[1]
		else :
			bluex = unwrappedPt1[0]
			bluey = unwrappedPt1[1]
			redx = unwrappedPt2[0]
			redy = unwrappedPt2[1]
		centerx = (bluex+redx)/2.0
		centery = (bluey+redy)/2.0
		theta = math.atan2(bluey-redy, bluex-redx)
		return [keypoints[0].pt[0]+refPt[0], keypoints[0].pt[1]+refPt[1]], [centerx, centery], theta
	else :
		return False, False, False
		

def processImage(img, refPt):
	
	img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY )

	#simple threshold
	ret,img_thresh = cv2.threshold(img_gray,140,255,cv2.THRESH_BINARY)
	img_thresh_2 = cv2.dilate(img_thresh, np.ones((3, 3)))

	# Set up the detector with default parameters.
	params = createSimpleBlobDetectorParams()
	
	ver = (cv2.__version__).split('.')
	if int(ver[0]) < 3 :
		detector = cv2.SimpleBlobDetector(params)
	else : 
		detector = cv2.SimpleBlobDetector_create(params)
 
	# Detect blobs.
	keypoints = detector.detect(img_thresh_2)
	
	return processKeypoints(keypoints, img, refPt)
		
def unwrap(pt, refPt):
	M = [[4.21412876e-01,1.63141220e-01,-1.43069743e+02],[2.20151807e-02,9.69559655e-01,-7.60938354e+01],[1.17752302e-05,1.46472177e-03,1.00000000e+00]]
	x = pt[0] + refPt[0]
	y = pt[1] + refPt[1]
	x2 = (M[0][0]* x + M[0][1] * y + M[0][2]) / (M[2][0]* x + M[2][1] * y + M[2][2])
	y2 = (M[1][0]* x + M[1][1] * y + M[1][2]) / (M[2][0]* x + M[2][1] * y + M[2][2])
	return [x2, y2]
	
# --------------------------------------------------------

# COMMUNICATION 

import socket

UDP_IP = "192.168.16.195"
UDP_PORT = 5005

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

# --------------------------------------------------------


# Create a pool of image processors
done = False
lock = threading.Lock()
counterLock = threading.Lock()
start = time.time()
frameCounter = 0
pool = []


class ImageProcessor(threading.Thread):
	def __init__(self):
		super(ImageProcessor, self).__init__()
		self.stream = io.BytesIO()
		self.event = threading.Event()
		self.terminated = False
		self.start()
		self.START_POINT = [570,199]
		self.EXPLORATION_ZONE=[100,100]
		self.pt = self.START_POINT
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		

	def run(self):
		# This method runs in a separate thread
		global done
		global frameCounter
		global start
		global sock
		while not self.terminated:
			# Wait for an image to be written to the stream
			if self.event.wait(1):
				try:
					self.stream.seek(0)
					# Read the image and do some processing on it
					# Read the stream. Each frame from this video stream is a jpeg image.
					data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
					
					xmin = max(0, int(round(self.pt[0]))-self.EXPLORATION_ZONE[0])
					ymin = max(0, int(round(self.pt[1]))-self.EXPLORATION_ZONE[1])
					xmax = min(1295, int(round(self.pt[0]))+self.EXPLORATION_ZONE[0])
					ymax = min(971, int(round(self.pt[1]))+self.EXPLORATION_ZONE[1])

					
					# "Decode" the jpeg image to a BGR array. This step is quite
					# processing heavy (about 80-150% CPU depending on image details)
					image = cv2.imdecode(data, 1)
					
					# Run the image processing on roi
					self.pt, center, theta = processImage(image[ymin:ymax, xmin:xmax], [xmin, ymin])
					
					if (not self.pt):
						# if no robot is found with partial image, process full image
						self.pt, center, theta = processImage(image, [0, 0])
						
					if (self.pt):
						message = "{:0.2f},{:0.2f},{:0.2f}".format(center[0], center[1], theta)
						print "robot found at " + message
						self.sock.sendto(message, (UDP_IP, UDP_PORT))
					
					if (not self.pt):
						# prevent no robot condition to become cpu-hungry
						time.sleep(0.5)
						self.pt = self.START_POINT
					
					counterLock.acquire()
					frameCounter += 1
					if ((frameCounter % 40) == 0):
						end = time.time()
						print "FPS {0:0.2f}".format(40/(end - start))
						start = time.time()
					counterLock.release()
					#...
					#...
					# Set done to True if you want the script to terminate
					# at some point
					#done=True
				finally:
					# Reset the stream and event
					self.stream.seek(0)
					self.stream.truncate()
					self.event.clear()
					# Return ourselves to the pool
					with lock:
						pool.append(self)

def streams():
	while not done:
		with lock:
			if pool:
				processor = pool.pop()
			else:
				processor = None
		if processor:
			yield processor.stream
			processor.event.set()
		else:
			# When the pool is starved, wait a while for it to refill
			time.sleep(0.1)

with picamera.PiCamera() as camera:
	pool = [ImageProcessor() for i in range(4)]
	
	# initialize the camera and grab a reference to the raw camera capture
	camera.resolution = (1296,972)
	camera.framerate = 20
	# Set ISO to the desired value
	camera.iso = 800
	# Wait for analog_gain to set to something greater than 1 before setting exposure_mode to off
	time.sleep(5.0)
	# Fix Automatic White Balance and shutter speed
	camera.shutter_speed = camera.exposure_speed
	camera.exposure_mode = 'off'
	camera.awb_mode = 'off'
	camera.awb_gains = (1.5, 1.5)

	camera.capture_sequence(streams(), use_video_port=True)

# Shut down the processors in an orderly fashion
while pool:
	with lock:
		processor = pool.pop()
	processor.terminated = True
	processor.join()