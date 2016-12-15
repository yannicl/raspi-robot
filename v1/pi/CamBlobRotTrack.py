import sched, time, math
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
img = cam.getImage().rotate(180)

class Robot:
    def goForward(self):
        ser.write("A,0,160,0,200,S")
    def goBackward(self):
        ser.write("A,1,160,1,200,S")
    def turnLeft(self):
        ser.write("A,0,200,1,200,S")
    def turnRight(self):
        ser.write("A,1,200,0,200,S")
    def stop(self):
        ser.write("A,0,000,0,000,S")

robot = Robot()


def width_real(width, pos_y):
    return 12.0/320.0*357.0*width/pos_y

def distance_real(pos_y):
    return -6.417e-6*math.pow(pos_y, 3) + 5.874e-3*math.pow(pos_y,2)-1.889*pos_y+241.669

while(1):
    img = cam.getImage().rotate(180)
    imgg = img.grayscale()
    imggt = imgg.threshold(100)
    blobs = imggt.findBlobs()
    
    if (blobs and len(blobs) > 0):
        centroid = blobs[-1].centroid()
        x = centroid[0]
        y = centroid[1]
        angle = (x - 320.0) / y
        area = blobs[len(blobs)-1].area()
        print 'A {0:0.2f} {1:0.2f} {1:0.2f}'.format(blobs[-1].area(), x, y)
        width_r = width_real(blobs[-1].width(), y)
        distance_r = distance_real(y)
        print 'D {0:0.2f} {1:0.2f} {2:0.2f}'.format(width_r, distance_r, angle)
        if (math.fabs(angle)> 0.2):
            if (angle < 0):
                robot.turnLeft()
            else:
                robot.turnRight()
        if (distance_r > 16):
            if (distance_r > 36):
                robot.goForward()
            elif (distance_r < 24):
                robot.goBackward()
                


