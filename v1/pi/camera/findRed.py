from SimpleCV import Camera
from SimpleCV import Color

cam = Camera()

while True:
    img = cam.getImage()
    red_box = img.colorDistance(Color.RED)
    red_blobs = red_box.findBlobs()
