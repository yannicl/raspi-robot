import sched, time, threading
import serial
from tendo import singleton
from SimpleCV import *

me = singleton.SingleInstance() # will sys.exit(-1) if another instance is running

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

# Init serial
ser = serial.Serial('/dev/ttyUSB0', 57600)
ser.write("A,0,000,0,000,S")


# Init SimpleCV
cam = SimpleCV.Camera()
js = SimpleCV.JpegStreamer(8989)
img = cam.getImage().rotate(180)
img.save(js, "jpeg")


while (1):
    img = cam.getImage().rotate(180)
    img.save(js, "jpeg")
    time.sleep(0.1)

