import sys
import os
import argparse
import random
import xml.etree
from xml.etree import ElementTree
import nltk
import re

try:
    import ssl
except ImportError:
    print "error: no ssl support"

import urllib2
import libxml2
from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):
    datafields = []    

    def handle_data(self, data):
        self.datafields.append(data)

    def get_data(self):
        return ' '.join(self.datafields)

    def clean(self):
        self.datafields = []

def get_raw_html_libcurl(request_url, user_agent):
    import pycurl
    import StringIO
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, request_url)
    curl.setopt(pycurl.HEADER, 0)
    curl.setopt(pycurl.REFERER, 'http://localhost')
    curl.setopt(pycurl.SSL_VERIFYPEER, False)
    curl.setopt(pycurl.user_agent, user_agent)
    curl.setopt(pycurl.FOLLOWLOCATION, True)

    result_stringio = StringIO.StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, result_stringio.write)

    try:
        curl.perform()
    except:
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()

    return result_stringio.getvalue()


def get_raw_html_urllib(request_url, user_agent):
    #req = urllib2.urlopen( request_url )
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', user_agent)]
    response = opener.open(request_url)
    return response.read()

def remove_containing_word(s, words):
    for w in words:
        s = re.sub('[^ ]*%s[^ ]*' % w, '', s)
    return s

def sanitize_result(s):
    #s = remove_containing_word(s, ['http://', 'www\.']    )
    #s = remove_containing_word(s, ['\.com', '\.org', '\.net'])
    #s = remove_containing_word(s, ['\.jpg', '\.jpeg', '\.png'] )
    #s = re.sub("[^a-zA-Z0-9 -]+", "", s)
    s = re.sub('[\(\)\%]+', '', s)
    tokens = nltk.word_tokenize(s)
    tagged_tokens = nltk.pos_tag( tokens )
    grammar = "NP: {(<NN>|<NNP>|<NNS>)+}"
    cp = nltk.RegexpParser(grammar)
    parsed_sentence = cp.parse(tagged_tokens)
    terms = []
    for e in parsed_sentence:
        if not isinstance(e,tuple):
            for term in e:
                if len(term[0])>1:
                    terms.append( term[0] )
       
    s = ' '.join(terms)
    s = s.lower()

    return s
 

def get_simple_xpath( doc, xpath ):
    ctxt = doc.xpathNewContext()
    xp_results  = ctxt.xpathEval(xpath)
    results = []
    i = 0
    parser = MyHTMLParser()
    parser.clean()
    for xp in xp_results:
        parser.feed( str(xp) )
    
    ctxt.xpathFreeContext()

    return sanitize_result(parser.get_data())

#######################################

parser = argparse.ArgumentParser(description='Google image-by-image scraper')
parser.add_argument('--plainoutput', action='store_true')
parser.add_argument('urls', metavar='url', help='some URLS to images', nargs='+')
parser.add_argument('--verbose', action='store_true')
parser.add_argument('--gisroot', help='do not change unless you know what you are doing', default='https://www.google.com/searchbyimage?&image_url=')
args = parser.parse_args()

xpath = {}

xpath['bestguess'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@id='rcnt']/div[@class='col'][2]/div[@id='center_col']/div[@id='res']/div[@id='topstuff']/div[@class='card-section']/div[@class='qb-bmqc']/a[@class='qb-b']"

xpath['desc'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@id='rcnt']/div[@class='col'][3]/div[@id='rhscol']/div[@id='rhs']/div[@id='rhs_block']/ol/li[@class='g mnr-c rhsvw g-blk']/div[@class='kp-blk _m2 _Lv _KO']"

# this xpath was built by removing explicit element access (just get several xpaths and try to see a pattern) 
xpath['summaries'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@id='rcnt']/div[@class='col'][2]/div[@id='center_col']/div[@id='res']/div[@id='search']/div[@id='ires']/ol[@id='rso']/div[@class='srg']/li[@class='g']/div[@class='rc']/div[@class='s']/div/span[@class='st']" 

xpath['titles'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@id='rcnt']/div[@class='col'][2]/div[@id='center_col']/div[@id='res']/div[@id='search']/div[@id='ires']/ol[@id='rso']/div[@class='srg']/li[@class='g']/div[@class='rc']/h3[@class='r']/a"


scrapeResults = {}
for image_url in args.urls:
    image_url_escaped = urllib2.quote(image_url,'')
    request_url = args.gisroot + image_url_escaped

    # select user agent
    with open('useragents.txt', 'r') as uafile:
        user_agents = uafile.readlines()
    user_agent = random.choice(user_agents).rstrip()

    if args.verbose:
        print "Search URL: ", request_url
        print "UA: ", user_agent

    gis_raw_result = get_raw_html_urllib( request_url, user_agent )

    parse_options = libxml2.HTML_PARSE_RECOVER + libxml2.HTML_PARSE_NOERROR + libxml2.HTML_PARSE_NOWARNING

    doc = libxml2.htmlReadDoc( gis_raw_result, '', None, parse_options)

    scrapeResult = {}
    for key in xpath:
        r = get_simple_xpath(doc, xpath[key])
        scrapeResult[key] = r

    scrapeResults[image_url] = scrapeResult
    
    doc.freeDoc()


if args.plainoutput:
    for imagefn in scrapeResults:
        print
        print imagefn
        for key in scrapeResults[imagefn]:
            print key, ": ", scrapeResult[key]
else:
    import json
    print json.dumps( scrapeResults, indent=4, sort_keys=False)



