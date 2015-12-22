# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 13:06:06 2015

An Article object that holds information about a scientific article obtained
from the Internet.

@author: Alek
@version: 1.0.0
@since: Sat Oct  3 13:06:06 2015

CHANGELOG:
Sat Oct  3 13:06:06 2015 - 1.0.0 - Alek - Issued the first version based on a class previously defined elsewhere.
"""

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
        
    def __str__(self):
        return "{}, {} ({})".format(self.Authors, self.Title, self.Year)