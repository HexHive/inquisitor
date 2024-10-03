#!/usr/bin/python3
'''
The goal of this script is to match the reviewer names and emails to the names used in DBLP
'''
import lxml.etree as ET
from gzip import GzipFile
import pickle
import csv
import re
import sys
from datetime import datetime

class Author():
    def __init__(self, name, email, orcid, dblp):
        self.name = name
        self.email = email
        self.orcid = orcid
        self.dblp = dblp
        self.coauthors = {}
        current_year = datetime.now().year
        for i in range(0,6):
            self.coauthors[current_year-i] = []

def load_reviewers(reviewer_file):
    reviewers = {}
    with open(reviewer_file, 'r') as f:
        reviewer_file_csv = csv.reader(f)
        for row in reviewer_file_csv:
            aut = Author(row[0], row[1], row[2], row[3])
            #reviewers[row[0]+' '+row[1]] = aut
            reviewers[row[3]] = aut
    return reviewers

def parse_dblp(dblp_file, reviewers):
    dblp_stream = GzipFile(filename=dblp_file)
    authors = []
    in_pub = False # flag marking if we're parsing a publication
    in_www = False # flag marking if we're parsing affiliation information
    year = 0
    current_year = datetime.now().year
    for event, elem in ET.iterparse(dblp_stream, events = ('start', 'end',), load_dtd = True):
        # mark header tags
        if event == 'start':
            if elem.tag == 'inproceedings' or elem.tag == 'article':
                in_pub = True
            if elem.tag == 'www':
                in_www = True
        # process individual closing tags
        if event == 'end':            
            if (in_pub or in_www) and elem.tag == 'author':
                authors.append(elem.text)
            elif in_pub and elem.tag == 'year':
                year = int(elem.text)
            elif elem.tag == 'inproceedings' or elem.tag == 'article':
                if year >= current_year - 5 and year <= current_year:
                    for author in authors:
                        if author in reviewers:
                            for coauthor in authors:
                                if coauthor != author and coauthor not in reviewers[author].coauthors[year]:
                                    reviewers[author].coauthors[year].append(coauthor)
                authors = []
                year = 0
                in_pub = False
            elif elem.tag == 'www':
                authors = []
                year = 0
                in_www = False
            elem.clear()


if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print('Find coauthors of mapped HotCRP reviewers. Run the script with: python3 {} hotcrp-users-mapped.csv [dblp.xml.gz]'.format(sys.argv[0]))
        exit(1)
    # Parse reviewers from HotCRP CSV
    reviewers = load_reviewers(sys.argv[1])

    if len(sys.argv) == 2:
        dblp_file = './dblp.xml.gz'
    else:
        dblp_file = sys.argv[2]
    parse_dblp(dblp_file, reviewers)

    current_year = datetime.now().year
    for reviewer in reviewers:
        print('{} -> {} {} {} {} {} {}'.format(reviewer, len(reviewers[reviewer].coauthors[current_year]), len(reviewers[reviewer].coauthors[current_year-1]), len(reviewers[reviewer].coauthors[current_year-2]), len(reviewers[reviewer].coauthors[current_year-3]), len(reviewers[reviewer].coauthors[current_year-4]), len(reviewers[reviewer].coauthors[current_year-5])))


    with open(sys.argv[1][:-4]+'.pickle', 'wb') as f:
        pickle.dump(reviewers, f)
        f.close()

