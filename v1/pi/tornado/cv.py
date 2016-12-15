from SimpleCV import *

cam = SimpleCV.Camera()
for i in range(0,10):
    img = cam.getImage()
    img.save("cam_" + str(i) + ".png")

