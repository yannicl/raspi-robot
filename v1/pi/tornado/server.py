import tornado.ioloop
import tornado.web
import tornado.websocket
import socket
import thread

from tornado.options import define, options, parse_command_line

# ---- Global variables

webSockets = []

# -------- UDP position listener -------
def listen_udp():
	UDP_IP = "192.168.16.195"
	UDP_PORT = 5005
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	global udpFrame
	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
		values = data.split(',')
		for ws in webSockets:
			ws.write_message('{{"x":{}, "y":{}, "theta":{}}}'.format(values[0], values[1], values[2]))

thread.start_new_thread(listen_udp, ())		


# -------- Web Server -------

define("port", default=8888, help="run on the given port", type=int)




# ---------

class IndexHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.render("index.html")
		#we don't need self.finish() because self.render() is followed by self.finish() inside tornado
		#self.finish()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True
	def open(self, *args):
		webSockets.append(self)
		self.stream.set_nodelay(True)
		print "open"

	def on_message(self, message):		
		print "nop"
		
	def on_close(self):
		webSockets.remove(self)
		print "close"

app = tornado.web.Application([
	(r'/raspi-robot', IndexHandler),
	(r'/raspi-robot/coord', WebSocketHandler),
])

if __name__ == '__main__':
	parse_command_line()
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
