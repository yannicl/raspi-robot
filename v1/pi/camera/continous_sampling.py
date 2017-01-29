# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
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

rawCapture = PiRGBArray(camera, size=(1296,972))

i = 0 
j = 0

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	
	filename = "ss_large_%06d.png" % i
	print "writing frame to " + filename
	cv2.imwrite(filename, image)

	i = i + 1
  
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 