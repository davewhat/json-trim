import SocketServer
import BaseHTTPServer
import urllib
import httplib
import json
import re
import thread

from trim import *

PORT = 8080

FILTERS = [
("/activities/recent", "filter_activities_recent.json")
]

class Proxy(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self, mode='GET', post_data = None):
		conn = httplib.HTTPSConnection('api.foursquare.com')
		req_headers = {}
		if mode=='POST':
			req_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
		conn.request(mode, self.path, post_data, req_headers)
		resp = conn.getresponse().read()
		for filter_pair in FILTERS:
			if self.path.find(filter_pair[0]) != -1:
				print("applying " + filter_pair[1])
				f = open(filter_pair[1], 'r')
				filter = json.loads(re.sub('\t', '', re.sub('\n','',f.read())))
				resp_json = json.loads(resp)				
				strip(resp_json, filter, self.debug_mode)
				resp = json.dumps(resp_json)		
		self.protocol_version = 'HTTP/1.1'
		self.send_response(200)
		self.send_header('Content-Length', str(len(resp) + 1))
		self.wfile.write('\n\n')
		self.wfile.write( resp )
		
	def do_POST(self):
		post_data = self.rfile.read(int(self.headers['Content-Length']))
		self.do_GET('POST', post_data)

class DebugProxy(Proxy):
	debug_mode = True

class RegularProxy(Proxy):
	debug_mode = False


httpd = SocketServer.ForkingTCPServer(('', PORT), RegularProxy)
httpd_d = SocketServer.ForkingTCPServer(('', PORT+1), DebugProxy)

print 'serving at port', PORT
print '(debug at port', str(PORT+1) + ')'

thread.start_new_thread(httpd.serve_forever, ())
httpd_d.serve_forever()

