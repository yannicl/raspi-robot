import sched, time
import serial
from tendo import singleton
from SimpleCV import *

me = singleton.SingleInstance() # will sys.exit(-1) if another instance is running

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

# Init SimpleCV
cam = SimpleCV.Camera()
img = cam.getImage().rotate(180)

cntr = 0

while(1):
    cntr += 1
    img = cam.getImage().rotate(180)
    imgg = img.grayscale()
    imggt = imgg.threshold(80)
    blobs = imggt.findBlobs()
    
    if (blobs and len(blobs) > 0):
        centroid = blobs[-1].centroid()
        x = centroid[0]
        area = blobs[len(blobs)-1].area()
        print '{0:0.2f} {1:0.2f}'.format(blobs[-1].area(), x)
    else:
        print '{0:d}'.format(cntr)
        
