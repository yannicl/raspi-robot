import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options, parse_command_line
from SimpleCV import *
from math import sqrt

define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()
cam = SimpleCV.Camera()
RED=100,0,0

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        #self.write("This is your response")
        self.render("index.html")
        #we don't need self.finish() because self.render() is followed by self.finish() inside tornado
        #self.finish()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        clients[self.id] = {"id": self.id, "object": self}

    def on_message(self, message):        
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        print "Client %s received a message : %s" % (self.id, message)
        img = cam.getImage()
        img_rb = img.colorDistance(RED).threshold(20).invert()
        blobs = img_rb.findBlobs()
        circleLayer = DrawingLayer((img.width,img.height))        
        
        if (blobs and len(blobs) >= 1):
            centroid = blobs[len(blobs)-1].centroid()
            area = blobs[len(blobs)-1].area()
            circleLayer.circle(centroid,sqrt(area))
            img.addDrawingLayer(circleLayer)
            self.write_message("Block found at x:" + str(centroid[0]) + ", y:" + str(centroid[1]))
        else:
            self.write_message("No block found")

        img.show()

        
    def on_close(self):
        if self.id in clients:
            del clients[self.id]

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/websocket', WebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
