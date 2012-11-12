import SocketServer
import BaseHTTPServer
import urllib
import httplib
import json
import re

from trim import *

PORT = 8080

FILTERS = [
("/activities/recent", "filter_activities_recent.json")
]

class Proxy(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self, mode='GET'):
		print("path: " + self.path)
		conn = httplib.HTTPSConnection('api.foursquare.com')
		conn.request(mode, self.path)
		resp = conn.getresponse().read()
		for filter_pair in FILTERS:
			if self.path.find(filter_pair[0]) != -1:
				print("applying " + filter_pair[1])
				f = open(filter_pair[1], 'r')
				z = re.sub('\t', '', re.sub('\n','',f.read()))
				filter = json.loads(z)
				resp_json = json.loads(resp)				
				strip(resp_json, filter, True)
				resp = json.dumps(resp_json)		
		self.wfile.write( resp )
		
	def do_POST(self):
		self.do_GET('POST')


httpd = SocketServer.ForkingTCPServer(('', PORT), Proxy)
print 'serving at port', PORT
httpd.serve_forever()