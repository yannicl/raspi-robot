import tornado.ioloop
import tornado.web
import tornado.websocket
from SimpleCV import *

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = dict()
cam = SimpleCV.Camera()

RED=100,0,0
js = SimpleCV.JpegStreamer(8989)
img = cam.getImage().rotate(180)
img.save(js, "jpeg")

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        #self.write("This is your response")
        self.render("imageServer.html")
        #we don't need self.finish() because self.render() is followed by self.finish() inside tornado
        #self.finish()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
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
        self.write_message("Hello World!");
        
    def on_close(self):
        if self.id in clients:
            del clients[self.id]

class ImageWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    def open(self, *args):
        self.stream.set_nodelay(True)

    def on_message(self, message):
        img = cam.getImage().rotate(180)
        #img_rb = img.colorDistance(RED).threshold(20).invert()
        img_rb = img.hueDistance(SimpleCV.Color.RED).threshold(20).invert()
        blobs = img_rb.findBlobs()
        circleLayer = DrawingLayer((img.width,img.height))
        
        
        if (blobs and len(blobs) >= 1):
            centroid = blobs[len(blobs)-1].centroid()
            area = blobs[len(blobs)-1].area()
            circleLayer.circle(centroid,int(sqrt(area/3.14)),SimpleCV.Color.RED)
            img.addDrawingLayer(circleLayer)
            self.write_message('{"position":{"x":' + str(centroid[0]) + ', "y":' + str(centroid[1]) + '}}')
        else:
            self.write_message("No block found")        

        img.save(js, "jpeg")
        
    def on_close(self):
        return

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/websocket', WebSocketHandler),
    (r'/imagews', ImageWebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
