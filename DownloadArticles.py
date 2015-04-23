# -*- coding: utf-8 -*-
"""
Test downloading scientific articles' infomration from the web.

Created on Sun Apr 19 20:46:55 2015

@author: alek
"""

import requests, re, difflib

" General regexes. "
IntegersParern = re.compile("\d+") # Any integer.
YearPattern = re.compile('\([0-9a-zA-Z\s]*\d{4}\)') # Any four-digit year encolsed in parentheses; may be preceded by a month in any format and also a day.
LinksPattern = re.compile('"((http|ftp)s?://.*?)"') # Will find URLs in a website text.

" CiteULike.org-specific regexes. "
TitlePattern = re.compile(';</span>.+</a></h2>') # A number of regexes designed to extract bits of information from the lines of CiteULike.org results website.
JournalPattern = re.compile('<i>[a-zA-Z\s\W\d]+</i>')
NoPattern = re.compile("No\.\s\d+")
VolPattern = re.compile("Vol\.\s\d+")
DOIPattern = re.compile(">doi\:[\W\w]+</a></div>")
AuthorPattern = re.compile('>[a-zA-Z\s.-]+</a>')
TagPattern = re.compile('>[a-zA-Z]+</a>')
ArticleIDsPattern = re.compile('<tr class="list {article_id:\d+}" data-article_id=\d+>') # Will find the beginnings of the articles from CIteULike.org.

" Google Scholar-specific regexes. "
CitedByPattern = re.compile('cites=\d+') # Will find those parts of the links that enable the papers that cite a given article to be displayed on Google Scholar.
TitlePatternGoogle = re.compile('nossl=1">[\s\w\d\:\-\,\.\;\&\#]+</a></h3>') # Just think of all the stuff people might put in titles... Also sometimes Google will put weird stuff like &#8208; instead of -, which probably has to do with encoding. But I know too little about this to fix it.
YearPatternGoogle = re.compile('\,\s\d{4}[\s\-<]*')
ArticleInfoPatternGoogle = re.compile('[\.\,\-\s\w]+\,\s\d{4}[\s\-<]*') # Will find the list of authors, journal, and year.
CitedByNumberPattern = re.compile('Cited\sby\s\d+') # How many times the given article has been cited.

class Article(object):
    def __init__(self, title, authorList, year, journal, doi="", volume=-1, number=-1, tagList=[], abstract="", citeULikeID=-1):
        """ Initialise an Article class that holds the information about a scientific
        article.
        
        Arguments
        ----------
        title - str with the title of the artcile.
        authorList - list of str with author names, can have initials.
        year - int with the publishing year.
        journal - str with the title of the journal where the article was published.
        doi - str with the DOI (Digital Object Identifier) of the article.
        volume - volume of the journal where the article was published.
        number - issue of the journal where the article was published.
        tagList - list of str with keywords of the article.
        abstract - str with the abstract of the article.
        citeULikeID - int with the ID from CiteULike.org.
        
        Guaranteed Attributes
        ----------
        Title - str with the title of the artcile.
        Authors - list of str with author names, can have initials.
        Year - int with the publishing year.
        Journal - str with the title of the journal where the article was published.
        
        Optional Attributes
        ----------
        DOI - str with the DOI (Digital Object Identifier) of the article, e.g.
            10.1103/physrev.28.727; empty string if not supplied.
        Vol - volume of the journal where the article was published;
            999 if unknown.
        No - issue of the journal where the article was published; 999 if unknown.
        Keywords - list of str with keywords of the article; empty list if unknown.
        Abstract - str with the abstract of the article; empty string if unkown.
        CiteULikeID - int with the ID from CiteULike.org.
        """
        self.CiteULikeID = citeULikeID
        self.Title = title
        self.Authors = authorList
        self.Year = year
        self.Journal = journal
        self.DOI = doi
        self.Vol = volume
        self.No = number
        self.Keywords = tagList
        self.Abstract = abstract

def getCitingArticles( article, pageLimit=2 ):
    """ Find the artciles and books that quote a given article and return them.
    Arguments
    ----------
    article - An instance of Artice (@see Article) quotations of which are to be found.
    pageLimit - int, how many pages of the results will be searched.
    
    Returns
    ----------
    A list of Artciles that cite the input article.
    """
    HOME_URL = "https://scholar.google.co.uk/" # Home of Google Scholar.
    citingArticles = [] # List of articles that cite the input Article.
    
    " Search for the desired article. "
    searchURL = HOME_URL + "scholar?hl=en&q=" # Now we're searching for articles.
    searchURL += theArticle.Title # Search by title.
    the_page = requests.get(searchURL).text # Get the text version of the website. Use requests not urllib2 because the page will be too large for it.

    theArticleInfos = ArticleInfoPatternGoogle.findall(the_page) # Mixes of years, authors, and journal names of the Scholar search results looking for the input article.
    howManyTimesCited = CitedByNumberPattern.findall(the_page) # See how many times every article has been cited.
    howManyTimesCited = map(lambda x: int(x.lstrip("Cited by ")), howManyTimesCited) # Make it into integers.
    
    # Find the article from the many that will be displayed - will define articleID.
    articleID = 0 # Which article from the_page we're looking at.
    currentMaxCited = howManyTimesCited[ articleID ]
    currentHighestAuthorSimilarity = 0
    for i in range(len(howManyTimesCited)): # Articles that we have to look at to match to the article.
        if str(theArticle.Year) in theArticleInfos[i]: # This article is from the same year, promising.
            theArticleInfo = theArticleInfos[articleID].replace( str(theArticle.Year), "" )
            if difflib.SequenceMatcher(a="".join(theArticle.Authors).lower(), b=theArticleInfo.lower()).ratio() > currentHighestAuthorSimilarity: # The authors of this article look more like the authors of the input article.
                currentHighestAuthorSimilarity = difflib.SequenceMatcher(a="".join(theArticle.Authors).lower(), b=theArticleInfo.lower()).ratio()
                if howManyTimesCited[i] > currentMaxCited: # We're probably after the popular articles. Sometimes will get copies of the original article with fewer citations.
                    articleID = i # This is probably the article we're after.

    " Go through all the pages displaying the articles that cite the article. "
    citedByLinks = CitedByPattern.findall(the_page) # A list of links that take us to the pages displaying the articles that cite the articles displayed on the_page.
    citedByPageI = 0 # Page with the articles citing a given paper, ten per page.
    while citedByPageI <= pageLimit: # Unlikely that we'll get so many results but we don't want infinite loops, do we?
        citedByURL = HOME_URL + "scholar?start={}&".format(10*citedByPageI) # We'll display a website with articles that cite a given article.
        citedByURL += citedByLinks[articleID]
        citedBy_page = requests.get(citedByURL).text
        
        titlesCiting = TitlePatternGoogle.findall(citedBy_page) # Titles of articles that quote the article.
        yearsCiting = YearPatternGoogle.findall(citedBy_page)
    
        
        #TODO find the articles given by titlesCiting and yearsCiting on CiteULike and append them to citingArticles.
        
        citedByPageI += 1 # Go to the next results page.
        
    return citingArticles, titlesCiting, yearsCiting
    
def getArticlesCiteULike(authors=[""], keywords=[""], yearStart=1800, yearEnd=3000, title="", isbn="none", pageLimit=2):
    """ Find scientific articles that match given criteria on-line.
    
    Arguments
    ----------
    authors - list of strings with author names; can be surnames or surnames with
        names or initials.
    keywords - list of strings with the keywords to look for.
    yearStart - starting year of the published year bracket within which to find
        the articles.
    yearEnd - fina; year of the published year bracket within which to find
        the articles.
    title - string with the title of the article.
    isbn - str with the ISBN of the publication.
    pageLimit - int, how many pages of the results will be searched.
        
    Returns
    ----------
    A list of Articles @see Article.
    """
    pageNo = 1 # Number of the page with results.
    
    " Go through all the result pages we might get. "
    while pageNo <= pageLimit: # Unlikely that we'll get so many results but we don't want infinite loops, do we?
        " Build the search URL. "
        if not title: # We aren't looking for a specific title.
            BASE_SEARCH_URL = "http://www.citeulike.org/search/all/page/{}?q=".format( pageNo ) # All the search criteria are appended to this.
            searchURL = BASE_SEARCH_URL # Start from this and add all the search criteria.
            for tag in keywords:
                searchURL += "tag%3A"
                searchURL += '"{}"'.format(tag)
                searchURL += "+"
            for author in authors:
                searchURL += "author%3A"
                searchURL += '"{}"'.format(author) # author has to be in quotes.
                searchURL += "+"
            searchURL += "year%3A%5B{}+TO+{}%5D".format(yearStart,yearEnd)
            searchURL += "+isbn%3A{}".format(isbn)
        else: # The URL to look for specific titles is a bit different.
            BASE_SEARCH_URL = "http://www.citeulike.org/search/all/page/{}?q=title>".format( pageNo )
            searchURL = BASE_SEARCH_URL # Start from this and add all the search criteria.
            searchURL += title + "+"
            for tag in keywords:
                searchURL += "tag%3A"
                searchURL += '"{}"'.format(tag)
                searchURL += "+"
            for author in authors:
                searchURL += "author%3A"
                searchURL += '"{}"'.format(author) # author has to be in quotes.
                searchURL += "+"
            searchURL += "year%3A%5B{}+TO+{}%5D".format(yearStart,yearEnd)
            searchURL += "+isbn%3A{}".format(isbn)
        
        " Perform the actual search. "
        the_page = requests.get(searchURL).text # Get the text version of the website. Use requests not urllib2 because the page will be too large for it.
        
        lines = the_page.split("\n") # Parsing lines is easier than coming up with regexes to get the info about all the articles from the_page. Besides not every article will have all the information.
        
        # Initialise the artcile attributes.
        articleID=-1; articleTitle=""; authors=[]; year=0; journalTitle=""; doi=""; volume=-1; number=-1; tags=[]; abstract="";
        articles = [] # Articles we've found.
        firstArticle = True # If this is the first article we're reading.
        for i in range(len(lines)):
            if lines[i].startswith('<tr class="list {article_id:'):
                if firstArticle: # articleID and all the rest aren't defined yet.
                    articleID = int(IntegersParern.findall(lines[i])[0])
                    firstArticle = False
                else: # First add the artcile we've just parsed, then proceed to parsing the new one.
                    articles.append( Article(articleID, articleTitle, authors, year, journalTitle, doi, volume, number, tags, abstract) )
                    articleID = int(IntegersParern.findall(lines[i])[0])
            if '<a class="title"' in lines[i]:
                articleTitle = TitlePattern.findall(lines[i])[0].rstrip("</a></h2>").lstrip(";</span>")
            if "<a href='http://dx.doi.org" in lines[i]:
                try:
                    journalTitle = JournalPattern.findall(lines[i])[0].rstrip("</i>").lstrip("<i>")
                except IndexError:
                    print "\nNo journalTitle for:\n\t{}".format(lines[i])
                    journalTitle = "UNKNOWN JOURNAL"
                    
                try:
                    year = int( YearPattern.findall(lines[i])[0][-5:-1] ) # This may have a day and month in front, only extract the year (always last and followed by ")" ).
                except IndexError:
                    print "\nNo year for:\n\t{}".format(lines[i])
                    year = 0
                
                try:
                    volume = int(VolPattern.findall(lines[i])[0].lstrip("Vol. "))
                except IndexError:
                    print "\nNo volume for:\n\t{}".format(lines[i])
                    volume = -1
                
                try:
                    number = int(NoPattern.findall(lines[i])[0].lstrip("No. "))
                except (IndexError, ValueError):
                    print "\nNo number for:\n\t{}".format(lines[i])
                    number = -1
                
                doi = DOIPattern.findall(lines[i])[0].lstrip(">").rstrip("</a></div>")
            if '<a class="author"' in lines[i]:
                authors = map(lambda x: x.lstrip(">").rstrip("</a>"), AuthorPattern.findall(lines[i]))
            if '<span class="taglist">' in lines[i]:
                tags = map(lambda x: x.lstrip(">").rstrip("</a>"), TagPattern.findall(lines[i]))
            if '<h3>Abstract</h3>' in lines[i]:
                abstract = lines[i+1].lstrip("<p>").rstrip("</p>")
        # Add the last article.
        articles.append( Article(articleTitle, authors, year, journalTitle, doi, volume, number, tags, abstract, articleID) )

        pageNo += 1 # Go to the next results page.
        
    return articles

if __name__=="__main__": # If this is run as a stand-alone script run the verification/example searches.
#    " Example search for many articles. "
#    authors = ["langmuir", "tonks"] # Author names.
#    tags = ["langmuir", "probe"] # Tags we want to look for.
#    years = (1900,2015) # Year brackets we're interested in.
#    isbn = "none"
#    articles = getArticlesCiteULike(authors, tags, years[0], years[1], isbn)

    " Example search for articles citing a given article. "
    theArticle = Article("The Theory of Collectors in Gaseous Discharges", ["H.M. Mott-Smith", "Irving Langmuir"], 1926, "Physical Review", doi="10.1103/physrev.28.727", volume=28, number=4, citeULikeID=2534514)
    
#    citingArticles, titlesCiting, yearsCiting = getCitingArticles(theArticle)
    
    HOME_URL = "https://scholar.google.co.uk/" # Home of Google Scholar.
    citingArticles = [] # List of articles that cite the input Article.
    
    " Search for the desired article. "
    searchURL = HOME_URL + "scholar?hl=en&q=" # Now we're searching for articles.
    searchURL += theArticle.Title # Search by title.
    the_page = requests.get(searchURL).text # Get the text version of the website. Use requests not urllib2 because the page will be too large for it.

    theArticleInfos = ArticleInfoPatternGoogle.findall(the_page) # Mixes of years, authors, and journal names of the Scholar search results looking for the input article.
    howManyTimesCited = CitedByNumberPattern.findall(the_page) # See how many times every article has been cited.
    howManyTimesCited = map(lambda x: int(x.lstrip("Cited by ")), howManyTimesCited) # Make it into integers.
    
    # Find the article from the many that will be displayed - will define articleID.
    articleID = 0 # Which article from the_page we're looking at.
    currentMaxCited = howManyTimesCited[ articleID ]
    currentHighestAuthorSimilarity = 0
    for i in range(len(howManyTimesCited)): # Articles that we have to look at to match to the article.
        if str(theArticle.Year) in theArticleInfos[i]: # This article is from the same year, promising.
            theArticleInfo = theArticleInfos[articleID].replace( str(theArticle.Year), "" )
            if difflib.SequenceMatcher(a="".join(theArticle.Authors).lower(), b=theArticleInfo.lower()).ratio() > currentHighestAuthorSimilarity: # The authors of this article look more like the authors of the input article.
                currentHighestAuthorSimilarity = difflib.SequenceMatcher(a="".join(theArticle.Authors).lower(), b=theArticleInfo.lower()).ratio()
                if howManyTimesCited[i] > currentMaxCited: # We're probably after the popular articles. Sometimes will get copies of the original article with fewer citations.
                    articleID = i # This is probably the article we're after.
                
    " Go through all the pages displaying the articles that cite the article. "
    citedByPageI = 0 # Page with the articles citing a given paper, ten per page.
    citedByLinks = CitedByPattern.findall(the_page) # A list of links that take us to the pages displaying the articles that cite the articles displayed on the_page.
    while citedByPageI <= 2: # Unlikely that we'll get so many results but we don't want infinite loops, do we?
        citedByURL = HOME_URL + "scholar?start={}&".format(10*citedByPageI) # We'll display a website with articles that cite a given article.
        citedByURL += citedByLinks[articleID]
        citedBy_page = requests.get(citedByURL).text
        
        titlesCiting = TitlePatternGoogle.findall(citedBy_page) # Titles of articles that quote the article.
        yearsCiting = YearPatternGoogle.findall(citedBy_page)
        #TODO find the articles given by titlesCiting and yearsCiting on CiteULike and append them to citingArticles.
        for citingI in range(len(titlesCiting)): # Get every article that cites the article.
            candidateArticles = getArticlesCiteULike(yearStart=yearsCiting[citingI], yearEnd=yearsCiting[citingI], title=titlesCiting[citingI]) # This will return a list of candidate articles that match the search criteria. Find the one.
            currentBestCandidateArticleSimilarity = 0
            for candidateI in range(len(candidateArticles)):
                if difflib.SequenceMatcher(a=titlesCiting[citingI].lower(), b=candidateArticles[candidateI].Title.lower()).ratio() > currentBestCandidateArticleSimilarity:
                    currentBestCandidateArticleSimilarity = difflib.SequenceMatcher(a=titlesCiting[citingI].lower(), b=candidateArticles[candidateI].Title.lower()).ratio() # This is probably the citing article we're looking for.
        
        citedByPageI += 1 # Go to the next results page.