import SocketServer
import BaseHTTPServer
import urllib
import httplib
import json
import re
import thread
import urlparse

from trim import *

PORT = 8080

FILTERS = [
("/v2/activities/recent", "filter_activities_recent.json")
]

class Proxy(BaseHTTPServer.BaseHTTPRequestHandler):

	def performFiltering(self, filter_file_name, dictionary):
		print("applying " + filter_file_name)
		f = open(filter_file_name, 'r')
		filter = json.loads(re.sub('\t', '', f.read()))
		strip(dictionary, filter, self.debug_mode)

	def do_GET(self, mode='GET', post_data = None):
		conn = httplib.HTTPSConnection('api.foursquare.com')
		req_headers = {}
		if mode=='POST':
			req_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
		conn.request(mode, self.path, post_data, req_headers)
		response_object = conn.getresponse()
		resp = response_object.read()
		# given request path, look for filters to apply
		url_parsed = urlparse.urlparse(self.path)
		for filter_pair in FILTERS:
			# handle an exact match
			if url_parsed.path == filter_pair[0]:
				resp_dictionary = json.loads(resp)				
				self.performFiltering(filter_pair[1], resp_dictionary)
				resp = json.dumps(resp_dictionary)
			# handle /multi endpoint
			if url_parsed.path.find("/multi") != -1:
				url_prepend = url_parsed.path[:url_parsed.path.find("/multi")]
				# check each of the parallel requests for a match
				urlparse.parse_qs(url_parsed.query)['requests']
				for (c, r) in enumerate(urlparse.parse_qs(url_parsed.query)['requests'][0].split(',')):
					if url_prepend + urlparse.urlparse(r).path == filter_pair[0]:
						resp_dictionary = json.loads(resp)
						self.performFiltering(filter_pair[1], resp_dictionary['response']['responses'][c])
						resp = json.dumps(resp_dictionary)
		self.protocol_version = 'HTTP/1.1'
		self.send_response(200)
		self.send_header('Content-Length', str(len(resp) + 1))
		for (header, value) in response_object.getheaders():
			if not header.lower() in ['content-length', 'server', 'date']:
				self.send_header(header, value)
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

