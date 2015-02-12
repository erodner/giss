GISS: Google image-by-image search scraper
====================================

Google image-by-image search scraper in python to get the best guess result and webpage summaries with xpath queries.

Author: Erik Rodner (https://github.com/erodner)

Inspired by https://github.com/skyzer/google-reverse-image-search-scraper

WARNING AND DISCLAIMER: The code is only intended for research purposes and only for small-scale queries. Google will immediately block your requests, when you are
greedy (for good reason!), so use this code carefully and with proper reasoning. The authors do not take responsibility for any damage. Furthermore, the website structure
is changing continuously and in case you do not get any results, you need to modify the xpath queries in the code.

Usage
====================================

    usage: gis-scrape.py [-h] [--plainoutput] [--verbose] [--gisroot GISROOT]
                         [--useragents USERAGENTS]
                         url [url ...]

    Google image-by-image search scraper (GISS), authored by Erik Rodner

    positional arguments:
      url                   some URLS to images

    optional arguments:
      -h, --help            show this help message and exit
      --plainoutput         output the results in plain format rather than
      --verbose
      --gisroot GISROOT     do not change unless you know what you are doing
      --useragents USERAGENTS
                            file with a list of user agents (GISS is using a
                            random user agent everytime


Examples
====================================

Example call:

    python gis-scrape.py  'http://www.discoverlife.org/nh/tx/Cnidaria/images/Chrysaora_quinquecirrha,I_JP13_1.240.jpg' 'http://upload.wikimedia.org/wikipedia/commons/b/b6/Okapia_johnstoni_-Marwell_Wildlife,_Hampshire,_England-8a.jpg'

Example output in json format:

    {
        "http://upload.wikimedia.org/wikipedia/commons/b/b6/Okapia_johnstoni_-Marwell_Wildlife,_Hampshire,_England-8a.jpg": {
            "bestguess": "okapi animal", 
            "titles": "okapi wikipedia encyclopedia okapi san diego zoo animals congo forest giraffe okapi now endangered okapi okapia johnstoni rainforest alliance jacksonville zoo animals mammals okapi okapi forest giraffe okapia johnstoni artiodactyl okapi okapia johnstoni. mess reform", 
            "summaries": "okapi giraffe living members family giraffidae. the prominent attention speculation the okapi hindquarters legs nov okapi giraffe symbol zoo mexico okapi unknown scientists standing feet tall legs hindquarters photograph a.m. okapi watalinga animals areas. okapi okapia johnstoni artiodactyl ituri prominent attention speculation may giraffe okapi upright ears catch sounds avoid trouble. the okapi", 
            "desc": ""
        }, 
        "http://www.discoverlife.org/nh/tx/Cnidaria/images/Chrysaora_quinquecirrha,I_JP13_1.240.jpg": {
            "bestguess": "aurelia", 
            "titles": "aurelia wikipedia encyclopedia aurelia warleader gatherer wizards coast aurelia image discover life dna barcode life biotech scientific display zoological andy samberg uss indianapolis", 
            "summaries": "aurelia aur lia aurelija feminine name latin family name aurelius aureus meaning aurelia warleader. community rating community rating votes. click discover life page biology history ecology identification distribution aurelia image. aurelia spp. carybdea rastoni. cassiopeia spp. catosylus spp. chironex fleckeri. chiropsalmus quadrigatus. chiropsoides buitendijke. cyanea spp aurelia aurita cassiopea charybdaea chiropsalmus cubomedusa chrysaora halliclystus jelly aurelia moon shy clown towards. make eyes. hold breath. gospel tree dream summer aurelia moon shy clown towards. make eyes. hold breath. gospel tree dream summer", 
            "desc": "see results aurelia genus rank genus scientific name aurelia aurelia city iowa weather wind nw mph humidity local time tuesday pm"
        }
    }
