# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 13:06:06 2015

Parse results of Google Scholar search for specific terms. Original code from:
@see http://code.activestate.com/recipes/523047-search-google-scholar/#c2
I've updated it to BeautifulSoup4 and current syntax of Google Scholar source.
Also started saving the results in a class object for compatibility with other code.

@author: Alek
@version: 1.0.1
@since: Mon  5 Oct 15 18:38 2015

CHANGELOG:
Sat  3 Oct 15 13:06 - 1.0.0 - Alek - Issued the first version based on a class from the Internet.
Mon  5 Oct 15 18:38 - 1.0.1 - Alek - Now don't try to parse citations.
"""
import httplib, urllib, re
from bs4 import BeautifulSoup
import Article

IntegerPattern = re.compile('\s+\d+\s*') # Expects at least one whitespace in front the integer. May be followed by a whtitespace too.

class GoogleScholarSearchEngine:
    """ This class searches Google Scholar (http://scholar.google.com)

    Search for articles and publications containing terms of interest.
    
    Example
    ----------
    <tt>
    > from google_search import *\n
    > searcher = GoogleScholarSearch()\n
    > searcher.search(['breast cancer', 'gene'])
    </tt>
    """
    def __init__(self):
        """  Empty initialiser.
        """
        self.SEARCH_HOST = "scholar.google.com"
        self.SEARCH_BASE_URL = "/scholar"

    def search(self, searchTerms, limit=10):
        """ Searches Google Scholar using the specified terms.
        
        Returns a list of Artciles. Each Article contains the information related
        itin the following fields that every Article has:
            Title    : str, title of the publication
            Authors  : list of strings with author names (example: DF Easton, DT Bishop, D Ford)
            Journal  : str, name of the journal (example: Nature, Cancer Research)
            Year     : str, journal name & year (example: Nature, 2001)
            Keywords : list of strings with search terms used in the query
            Abstract : str, abstract of the publication
            
        Additional fields are added when creating the Articles here:
            JournalURL  : string with a link to the journal main website (example: www.nature.com),
                "Unavailable" if journal's URL is unkown.
            fullURL     : string with a link to the full text in HTML/PDF format,
                "Unavailable" if full text is unavailable
            pubURL      : string with a link to the publicly available version of the paper
            citingArticlesURL : string with a link to the site with articles citing this one
            relatedArticlesURL: string with a link to the site with articles related this one
                according to Google Scholar
            pubNoCitations    : number of times the publication is cited
            

        Arguments
        ----------
        @param searchTerms - list of strings that we'll search for.
        @param limit - int, maximum number of results to be returned (default=10).
        
        Returns
        ----------
        @return List of Articles (@see Article.Article), or an empty list if
            nothing is found.
        
        Raises
        ----------
        IOError when the connection to Google Scholar cannot be established.
        """
        params = urllib.urlencode({'q': "+".join(searchTerms), 'num': limit})
        url = self.SEARCH_BASE_URL+"?"+params # URL of the actual search with all the terms.
        return self.getArticlesFromPage( url, searchTerms)
        
    def getArticlesFromPage(self, url, searchTerms):
        """ Parses a given Google Scholar results page and returns a list of 
        Articles that are displayed there. This can be used to find citing or 
        related Articles using the citingArticlesURL or relatedArticlesURL fields.
        
        Returns a list of Artciles. Each Article contains the information related
        itin the following fields that every Article has:
            Title    : str, title of the publication
            Authors  : list of strings with author names (example: DF Easton, DT Bishop, D Ford)
            Journal  : str, name of the journal (example: Nature, Cancer Research)
            Year     : str, journal name & year (example: Nature, 2001)
            Keywords : list of strings with search terms used in the query
            Abstract : str, abstract of the publication
            
        Additional fields are added when creating the Articles here:
            JournalURL  : string with a link to the journal main website (example: www.nature.com),
                "Unavailable" if journal's URL is unkown.
            fullURL     : string with a link to the full text in HTML/PDF format,
                "Unavailable" if full text is unavailable
            pubURL      : string with a link to the publicly available version of the paper
            citingArticlesURL : string with a link to the site with articles citing this one
            relatedArticlesURL: string with a link to the site with articles related this one
                according to Google Scholar
            pubNoCitations    : number of times the publication is cited
            

        Arguments
        ----------
        @param url - str, URL to be appended to the self.SEARCH_HOST (i.e. scholar.google.com)
            to get to the results page (example: /scholar?q=related:X7dZ0Xg524gJ:scholar.google.com/&hl=en&as_sdt=0,5)
        @param limit - int, maximum number of results to be returned (default=10).
        
        Returns
        ----------
        @return List of Articles (@see Article.Article), or an empty list if
            nothing is found.
        
        Raises
        ----------
        IOError when the connection to Google Scholar cannot be established.
        """
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}

        conn = httplib.HTTPConnection(self.SEARCH_HOST)
        conn.request("GET", url, body=None, headers=headers)
        resp = conn.getresponse()
        
        if resp.status==200:
            html = resp.read()
            results = []
            html = html.decode('ascii', 'ignore') # Raw HTML file of the website with the search results.
            # Screen-scrape the result to obtain the publication information
            soup = BeautifulSoup(html)
            
            for record in soup.find_all('div',{'class': 'gs_r'}):#soup('p', {'class': 'g'}):
                if "[CITATION]" in record.text: # This isn't an actual article.
                    continue
                else:
                    allAs = record.find_all('a') # All <a></a> fields corresponding to this article.
    
                    " Get the public URL and the title, amybe full text URL if we're lucky. "
                    if len( allAs[0].find_all("span") ): # The first <a> has some <span> children.
                        fullURL = allAs[0].attrs['href'] # URL to the full text in HTML or PDF format (typically).
                        pubURL = allAs[1].attrs['href'] # This will be the public URL one gets when they click on the title.
                        pubTitle = allAs[1].text # Public URL has the title of the article as text.
                    else: # The first <a> of the result is the one with the title and public URL.
                        fullURL = "Unavailable" # No full text for this article... :(
                        pubURL = allAs[0].attrs['href']
                        pubTitle = allAs[0].text
                        
                    " Get the articles citing and related to this one. "
                    for a in allAs:
                        if "Cited by" in a.text:
                            pubNoCitations = int(  IntegerPattern.findall(a.text)[0] )
                            citingArticlesURL = a.attrs['href'] # Articles that cite this one.
                        elif "Related articles" in a.text:
                            relatedArticlesURL = a.attrs['href'] # URL to the related articles.
                    
                    " Get the authors; they're displayed in green, use it. "
                    authorPart = record.find('div',attrs={'class':'gs_a'}).text #record.first('font', {'color': 'green'}).string
                    if authorPart is None:    
                        authorPart = ''
                        # Sometimes even BeautifulSoup can fail, fall back to regex.
                        m = re.findall('<font color="green">(.*)</font>', str(record))
                        if len(m)>0:
                            authorPart = m[0]
    
                    " Get journal name, publication year, and authors' list. "
                    # Assume that the fields are delimited by ' - ', the first entry will be the
                    # list of authors, the last entry is the journal URL. We also have journal name and year there.
                    pubJournalYear = int(IntegerPattern.findall(authorPart)[0]) # We might get other integers, but not preceded by whitespaces.
                    
                    idx_start = authorPart.find(' - ') # Here the authors' list ends.
                    idx_end = authorPart.rfind(' - ') # Here the journal's public URL starts.
                    idx_jrnlNameEnd = authorPart.rfind(',') # After the journal name.
                    
                    pubJournalName = authorPart[idx_start:idx_jrnlNameEnd].lstrip().lstrip("-")
                    
                    pubAuthors = authorPart[:idx_start]                
                    pubJournalURL = authorPart[idx_end + 3:]
                    # If (only one ' - ' is found) and (the end bit contains '\d\d\d\d')
                    # then the last bit is journal year instead of journal URL
                    if pubJournalYear=='' and re.search('\d\d\d\d', pubJournalURL)!=None:
                        pubJournalYear = pubJournalURL
                        pubJournalURL = 'Unavailable'
                    
                    " Get the abstract. "
                    pubAbstract = record.find('div',attrs={'class':'gs_rs'}).text
                    
                    " Save the results. "
                    results.append( Article.Article(pubTitle,pubAuthors.split(','),pubJournalYear,pubJournalName,tagList=searchTerms,abstract=pubAbstract) )
                    # All the URLs.
                    results[-1].fullURL = fullURL
                    results[-1].pubURL = pubURL
                    results[-1].citingArticlesURL = citingArticlesURL
                    results[-1].relatedArticlesURL = relatedArticlesURL
                    # This might be useful to something, e.g. seeing whcih publications have the most impact.
                    results[-1].pubNoCitations = pubNoCitations
            return results
        else:
            raise IOError("Connection can't be established. Error code: {}, Reason: {}".format(resp.status,resp.reason))

if __name__ == '__main__':
    search = GoogleScholarSearchEngine()
    pubs = search.search(["breast cancer", "gene"], 10)
    for pub in pubs:
        print pub
        # This is how to get the citing abd related Articles.
#        search.getArticlesFromPage(pubs.citingArticlesURL,["breast cancer", "gene"],)