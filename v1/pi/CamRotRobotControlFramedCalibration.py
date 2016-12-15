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

class Robot:
    def goForward(self):
        ser.write("A,0,160,0,200,S")
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
    loopI = 15+1
    def setLoopI(self, value):
        self.loopI = value
    def getLoopI(self):
        return self.loopI
    def decrementLoopI(self):
        self.loopI -= 1

model = Model()

while (model.getLoopI() > 0):
    model.decrementLoopI()
    print '{0:3d} >'.format(model.getLoopI())
    robot.turnLeft()
    time.sleep(0.020)


#scheduler = sched.scheduler(time.time, time.sleep)

#def cam_loop(sc):
#    print '.'
#    img = cam.getImage().rotate(180)
#    
#    imgg = img.grayscale()
#    imggt = imgg.threshold(80)
#    blobs = imggt.findBlobs()
#    circleLayer = DrawingLayer((img.width,img.height))
#    
#    if (blobs and len(blobs) > 0):
#        centroid = blobs[-1].centroid()
#        x = centroid[0]
#        area = blobs[len(blobs)-1].area()
#        circleLayer.circle(centroid,int(sqrt(area/3.14)),SimpleCV.Color.RED)
#        img.addDrawingLayer(circleLayer)
#        #if (model.isLoopCamActive()):
#        print '{0:6d} {1:0.2f} {2:0.2f}'.format(model.getLoopI(), blobs[-1].area(), x)
#        
#    img.save(js, "jpeg")
#    scheduler.enter(0.150, 0.001, cam_loop, (sc,))
#scheduler.enter(0.150, 0.001, cam_loop, (scheduler,))

#scheduler.run()
