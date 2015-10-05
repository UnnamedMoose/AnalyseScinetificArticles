# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 17:58:41 2015

@author: artur
"""

import urllib2, copy
from bs4 import BeautifulSoup
from urlparse import urljoin

# what keywords to look out for
keywords = [
    'TerraPower',
    'Bill Gates',
    ]

# this will bookmark pages of interest
urlsOfInterest = []

# start list of urls to initiate the search
urls = [
#    'https://en.wikipedia.org/wiki/Portal:Contents',

#    'http://www.bbc.co.uk/news/business',
#    'http://www.nytimes.com/pages/business/index.html',
#    'http://www.theguardian.com/uk/business',
#    'http://www.forbes.com/business/',
#    'http://uk.reuters.com/business',
#    'http://www.independent.co.uk/news/business/news',
#    'http://www.telegraph.co.uk/finance/',
#    'http://www.washingtonpost.com/business/',

    'https://scholar.google.co.uk/scholar?cites=8829401031725111972&as_sdt=2005&sciodt=0,5&hl=en',
    ]

hdrs = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

# holds visited sites - avoid going around in circles
visited = copy.deepcopy(urls)

# keep looping until there are no more sites to search or stopping criteria has been reached
while (len(urls) > 0) and (len(visited) < 10000):
    # skip over invalid links
    try:
        # request the page, supply extra config stuff found on the web
        req = urllib2.Request(urls[0], headers=hdrs)
        
        # attempt to access the source of the current url - treat the urls list as a stack
        currentContent = urllib2.urlopen(req, timeout = 10).read()
        
        # search the contents for whatever may be of interest
        for key in keywords:
            if key in currentContent:
                print key, urls[0]
                if not urls[0] in urlsOfInterest:
                    urlsOfInterest.append(urls[0])
    except:
        currentContent = ''
    
    # remove the current url from the list of sites to search
    visited.append(urls[0])
    urls.pop(0)
    
    # create a soup
    soup = BeautifulSoup(currentContent)
    soup.prettify()
    
    # find all urls available on this site
    for tag in soup.findAll('a',href=True):
        # make the url absolute (e.g. add https://en.wikipedia.org at the beginning)
        link = urljoin(visited[-1], tag['href'])
        
        # keep this link for future searches only if it's not been visited before
        if link and link not in visited:
            urls.append(link)
    
    print "Searched {:d} sites, have {:d} on the stack".format(len(visited),len(urls))
    