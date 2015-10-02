# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 17:58:41 2015

@author: artur
"""

import urllib2, copy
from bs4 import BeautifulSoup
from urlparse import urljoin

# start list of urls to initiate the search
urls = [
#    'https://en.wikipedia.org/wiki/Portal:Contents',
    'http://www.bbc.co.uk/news/business',
    'http://www.nytimes.com/pages/business/index.html',
    'http://www.theguardian.com/uk/business',
    'http://www.forbes.com/business/',
    'http://uk.reuters.com/business',
    'http://www.independent.co.uk/news/business/news',
    'http://www.telegraph.co.uk/finance/',
    'http://www.washingtonpost.com/business/',
    ]

# holds visited sites - avoid going around in circles
visited = copy.deepcopy(urls)

# keep looping until there are no more sites to search or stopping criteria has been reached
while (len(urls) > 0) and (len(visited) < 1000):
    # skip over invalid links
    try:
        # attempt to access the source of the current url - treat the urls list as a stack
        currentContent = urllib2.urlopen(urls[0], timeout = 1).read()
    except:
        currentContent = ''
    
    # remove the current url from the list of sites to search
    visited.append(urls[0])
    urls.pop(0)
    
    # create a soup
    soup = BeautifulSoup(currentContent)
    soup.prettify()
    
    # find all urls
    for tag in soup.findAll('a',href=True):
        # make the url absolute (e.g. add https://en.wikipedia.org at the beginning)
        link = urljoin(visited[-1], tag['href'])
        
        # keep this link for future searches only if it's not been visited before
        if link and link not in visited:
            urls.append(link)
    
    print "Searched {:d} sites, have {:d} on the stack".format(len(visited),len(urls))
    