#!/usr/bin/python3
'''
The goal of this script is to match the reviewer names and emails to the names used in DBLP.
Input: select reviewers from the user list in HotCRP and download the reviewer file.
'''
import lxml.etree as ET
from gzip import GzipFile
import pickle
import csv
import re
import sys

class Author():
    def __init__(self, name, email, orcid, dblp):
        self.name = name
        self.email = email
        self.orcid = orcid
        self.dblp = dblp

def get_reviewers(hotcrp_users):
    reviewers = []
    with open(hotcrp_users, 'r') as f:
        hotcrp_users_csv = csv.reader(f)
        for row in hotcrp_users_csv:
            if row[0] == 'given_name':
                continue
            aut = Author(row[0]+' '+row[1], row[2], row[5], [])
            #reviewers[row[0]+' '+row[1]] = aut
            reviewers.append(aut)
    return reviewers

def parse_dblp(dblp_file, reviewers):
    dblp_stream = GzipFile(filename=dblp_file)
    authors = []
    in_pub = False # flag marking if we're parsing a publication
    in_www = False # flag marking if we're parsing affiliation information

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
            elif elem.tag == 'inproceedings' or elem.tag == 'article':
                for author in authors:
                    for hc_author in reviewers:
                        if author != None and author.startswith(hc_author.name) and (len(author) == len(hc_author.name) or author[len(hc_author.name)] == ' '):
                            if not author in hc_author.dblp:
                                hc_author.dblp.append(author)
                                print('Found a match: HC {} -> {}'.format(hc_author.name, author))
                authors = []
                in_pub = False
            elif elem.tag == 'www':
                authors = []
                in_www = False
            elem.clear()


if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print('Map HotCRP reviewers to DBLP names. Run the script with: python3 {} hotcrp-users.csv [dblp.xml.gz]'.format(sys.argv[0]))
        exit(1)
    # Parse reviewers from HotCRP CSV
    reviewers = get_reviewers(sys.argv[1])

    if len(sys.argv) == 2:
        dblp_file = './dblp.xml.gz'
    else:
        dblp_file = sys.argv[2]
    parse_dblp(dblp_file, reviewers)

    for reviewer in reviewers:
        print('{} -> {}'.format(reviewer.name, len(reviewer.dblp)))


    with open(sys.argv[1][:-4]+'-mapped.csv', 'w') as f:
        mapped_csv = csv.writer(f)
        # rows in CSV: name in hotcrap, email, orcid, dblp_match1, dblp_match2, ...
        for reviewer in reviewers:
            row = [reviewer.name, reviewer.email, reviewer.orcid]
            row.extend(reviewer.dblp)
            mapped_csv.writerow(row)
        f.close()

