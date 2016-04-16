#!/usr/bin/env python
import sys
import urllib
import urllib2

# Read first commanline arg
temperature = sys.argv[1]

print "read " + temperature

url = 'http://localhost:8080/submit'

values = { 'temperature' : temperature,
           'pw' : 'hcpw' }

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
the_page = response.read()

print the_page
