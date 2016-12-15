import sched, time
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

class Robot:
    def goForward(self):
        ser.write("A,0,200,0,200,S")
    def goBackward(self):
        ser.write("A,1,200,1,200,S")
    def turnLeft(self):
        ser.write("A,0,200,1,200,S")
    def turnRight(self):
        ser.write("A,1,200,0,200,S")
    def stop(self):
        ser.write("A,0,000,0,000,S")

robot = Robot()

class Model:
    x = 320.0
    def setX(self, value):
        self.x = value
    def getX(self):
        return self.x

model = Model()
        

scheduler = sched.scheduler(time.time, time.sleep)

def robot_loop(sc):
    print '{0:0.2f}'.format(model.getX())
    if (model.getX() > 340):
        robot.turnRight()
    elif (model.getX() < 300):
        robot.turnLeft()
    else:
        robot.stop()
    scheduler.enter(0.250, 0.001, robot_loop, (sc,))

scheduler.enter(0.250, 0.001, robot_loop, (scheduler,))

def cam_loop(sc):
    img = cam.getImage().rotate(180)
    
    imgg = img.grayscale()
    imggt = imgg.threshold(80)
    blobs = imggt.findBlobs()
    circleLayer = DrawingLayer((img.width,img.height))
    
    if (blobs and len(blobs) > 0):
        centroid = blobs[-1].centroid()
        x = centroid[0]
        area = blobs[len(blobs)-1].area()
        circleLayer.circle(centroid,int(sqrt(area/3.14)),SimpleCV.Color.RED)
        img.addDrawingLayer(circleLayer)
        print '{0:0.2f} {1:0.2f}'.format(blobs[-1].area(), x)
        model.setX(x)
    img.save(js, "jpeg")
    scheduler.enter(0.250, 0.001, cam_loop, (sc,))
scheduler.enter(0.250, 0.001, cam_loop, (scheduler,))


scheduler.run()
