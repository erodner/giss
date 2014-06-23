import sys
import os
import argparse

try:
    import ssl
except ImportError:
    print "error: no ssl support"

import urllib2
import libxml2

google_gis_root_url = 'https://www.google.com/searchbyimage?&image_url=' 
image_url = sys.argv[1]
image_url_escaped = urllib2.quote(image_url,'')
request_url = google_gis_root_url + image_url_escaped

print "Search URL: ", request_url

import pycurl
curl = pycurl.Curl()
curl.setopt(pycurl.URL, request_url)
curl.setopt(pycurl.HEADER, 0)
#curl.setopt(pycurl.RETURNTRANSFER, 1)
curl.setopt(pycurl.REFERER, 'http://localhost')
curl.setopt(pycurl.SSL_VERIFYPEER, False)
#curl.setopt(pycurl.USERAGENT, $useragent)
curl.setopt(pycurl.FOLLOWLOCATION, True)

import StringIO
gis_raw_result = StringIO.StringIO()
curl.setopt(pycurl.WRITEFUNCTION, gis_raw_result.write)

try:
    curl.perform()
except:
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()

print gis_raw_result

#req = urllib2.urlopen( request_url )


#mydoc = ElementTree.fromstring(req.read())
#for e in mydoc.findall('//*'):
#    print e.get('title').text


parse_options = libxml2.HTML_PARSE_RECOVER + libxml2.HTML_PARSE_NOERROR + libxml2.HTML_PARSE_NOWARNING

doc = libxml2.htmlReadDoc(req.read(), '', None, parse_options)
print doc

links = doc.xpathEval('//a')
for link in links:
    href = link.xpathEval('attribute::href')
    if len(href) > 0:
        href = href[0].content
        print href
doc.freeDoc()

