#
# Google image-by-image search scraper
# Author: Erik Rodner, 2014
#
# This is research code only and should not be used to perform large-scale queries
#
#
#
import sys
import os
# command line parsing
import argparse
# random selection of user agents
import random
# XML/HTML parsing
import xml.etree
from xml.etree import ElementTree
import libxml2
from HTMLParser import HTMLParser
# naturual language tools for sanitizing results
import nltk
# regular expressions for sanitizing results
import re
# check for ssl availability in general
try:
    import ssl
except ImportError:
    print "error: no ssl support"
# library for performing HTTP(S) requests
import urllib2


""" Parser model to extract the content only and not the tags """
class MyHTMLParser(HTMLParser):
    datafields = []

    def handle_data(self, data):
        self.datafields.append(data)

    def get_data(self):
        return ' '.join(self.datafields)

    def clean(self):
        self.datafields = []

""" HTTP request with libcurl """
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

""" HTTP request with urllib (default) """
def get_raw_html_urllib(request_url, user_agent):
    #req = urllib2.urlopen( request_url )
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', user_agent)]
    response = opener.open(request_url)
    return response.read()

""" for manual sanitizing """
def remove_containing_word(s, words):
    for w in words:
        s = re.sub('[^ ]*%s[^ ]*' % w, '', s)
    return s

""" sanitizing results with natural language tools """
def sanitize_result(s):
    # manual sanitizing
    #s = remove_containing_word(s, ['http://', 'www\.']    )
    #s = remove_containing_word(s, ['\.com', '\.org', '\.net'])
    #s = remove_containing_word(s, ['\.jpg', '\.jpeg', '\.png'] )
    #s = re.sub("[^a-zA-Z0-9 -]+", "", s)

    # remove ), (, and %
    s = re.sub('[\(\)\%]+', '', s)
    if len(s)==0:
        return s

    # split into tokens
    tokens = nltk.word_tokenize(s)
    # tag the tokens
    tagged_tokens = nltk.pos_tag( tokens )
    # we only want to extract proper nouns, etc.
    grammar = "NP: {(<NN>|<NNP>|<NNS>)+}"
    # parse the tagged tokens
    cp = nltk.RegexpParser(grammar)
    parsed_sentence = cp.parse(tagged_tokens)
    # go through the parsing result and put everything into a string
    terms = []
    for e in parsed_sentence:
        if not isinstance(e,tuple):
            for term in e:
                if len(term[0])>1:
                    terms.append( term[0] )
    # join results and make everything lowercase
    s = ' '.join(terms)
    s = s.lower()

    return s

""" obtain all xpath results in a string """
def get_simple_xpath( doc, xpath ):
    ctxt = doc.xpathNewContext()
    # get xpath result
    xp_results  = ctxt.xpathEval(xpath)
    results = []
    i = 0
    # simply remove all tags
    parser = MyHTMLParser()
    parser.clean()
    for xp in xp_results:
        s = str(xp)
        if len(s)>0:
            parser.feed( s )

    ctxt.xpathFreeContext()
    # sanitize the results
    return sanitize_result(parser.get_data())

#######################################

# command line parser
parser = argparse.ArgumentParser(description='Google image-by-image search scraper (GISS), authored by Erik Rodner')
parser.add_argument('--plainoutput', action='store_true', help='output the results in plain format rather than')
parser.add_argument('urls', metavar='url', help='some URLS to images', nargs='+')
parser.add_argument('--verbose', action='store_true')
parser.add_argument('--gisroot', help='do not change unless you know what you are doing', default='https://www.google.com/searchbyimage?&image_url=')
parser.add_argument('--useragents', help='file with a list of user agents (GISS is using a random user agent everytime', default='useragents.txt')
args = parser.parse_args()

xpath = {}

# xpaths for different fields on the result page of Google image-by-image search
# if the interface is changed, this is the part that needs modification
# there are web browser plugins that provide you with proper xpaths
xpath['bestguess'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@class='mw']/div[@id='rcnt']/div[@class='col'][1]/div[@id='center_col']/div[@id='res']/div[@id='topstuff']/div[@class='card-section']/div[@class='_hUb']/a[@class='_gUb']"

xpath['desc'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@class='mw']/div[@id='rcnt']/div[@id='rhscol']/div[@id='rhs']/div[@id='rhs_block']/ol/li[@class='g mnr-c rhsvw kno-kp g-blk']/div[@class='kp-blk _Jw _Rqb _RJe']/div[@class='xpdopen']/div[@class='_OKe']/ol/li[@class='_DJe mod'][1]/div[@class='_cgc kno-fb-ctx']/div[@class='kno-rdesc']/span[1]"

# this xpath was built by removing explicit element access (just get several xpaths and try to see a pattern)
xpath['summaries'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@class='mw']/div[@id='rcnt']/div[@class='col'][1]/div[@id='center_col']/div[@id='res']/div[@id='search']/div/div[@id='ires']/ol[@id='rso']/div[@class='srg'][1]/li[@class='g']/div[@class='rc']/div[@class='s']/div/span[@class='st']"

xpath['summaries_alternative'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@id='rcnt']/div[@class='col'][2]/div[@id='center_col']/div[@id='res']/div[@id='search']/div[@id='ires']/ol[@id='rso']/li[@class='g'][1]/div[@class='rc']/div[@class='s']/div/span[@class='st']"

xpath['titles'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@class='mw']/div[@id='rcnt']/div[@class='col'][1]/div[@id='center_col']/div[@id='res']/div[@id='search']/div/div[@id='ires']/ol[@id='rso']/div[@class='srg']/li[@class='g']/div[@class='rc']/h3[@class='r']/a"

xpath['titles_alternative'] = "/html/body[@id='gsr']/div[@id='main']/div[@id='cnt']/div[@id='rcnt']/div[@class='col'][2]/div[@id='center_col']/div[@id='res']/div[@id='search']/div[@id='ires']/ol[@id='rso']/li[@class='g']/div[@class='rc']/h3[@class='r']/a"

# get list of user agents
with open(args.useragents, 'r') as uafile:
    user_agents = uafile.readlines()

# download all URLs, parse them, write results to the data dictionary
scrapeResults = {}
for image_url in args.urls:
    image_url_escaped = urllib2.quote(image_url,'')
    request_url = args.gisroot + image_url_escaped

    # select user agent
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


# output of the results
if args.plainoutput:
    for imagefn in scrapeResults:
        print
        print imagefn
        for key in scrapeResults[imagefn]:
            print key, ": ", scrapeResult[key]
else:
    import json
    print json.dumps( scrapeResults, indent=4, sort_keys=False)



