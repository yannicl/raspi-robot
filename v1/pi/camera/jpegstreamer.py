from SimpleCV import *
import time
c = Camera()
js = JpegStreamer(8888)

while(1):
    c.getImage().save(js)
    time.sleep(0.1);
