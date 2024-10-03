#!/usr/bin/python3
'''
The goal of this script is to match the reviewer names and emails to the names used in DBLP
You need two inputs from HotCRP on the paper overview:
- Reviews/Scores (CSV)
- Paper Information/Authors (CSV)
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

class Paper():
    def __init__(self, num, title, authors):
        self.num = num
        self.title = title
        self.authors = authors

def load_coauthors(coauthor_file):
    with open(coauthor_file, 'rb') as f:
        reviewers = pickle.load(f)
        f.close()
    return reviewers

def get_papers(authors_csv):
    papers = []
    with open(authors_csv, 'r') as f:
        hotcrp_users_csv = csv.reader(f)
        paper = None
        for row in hotcrp_users_csv:
            if row[0] == 'paper':
                continue
            if paper == None:
                paper = Paper(row[0], row[1], [row[2]+' '+row[3]])
                continue
            paper.authors.append(row[2]+' '+row[3])
            if row[0] != paper.num:
                papers.append(paper)
                paper = Paper(row[0], row[1], [row[2]+' '+row[3]])
        papers.append(paper)
    return papers

def check_conflicts(scores_csv, papers, reviewers):
    with open(scores_csv, 'r') as f:
        scores_csv = csv.reader(f)
        for row in scores_csv:
            if row[0] == 'paper':
                continue
            reviewer_email = row[5]
            paper_id = row[0]
            for paper in papers:
                if paper.num == paper_id:
                    break
            if paper.num != paper_id:
                print('Did not find reviews for {}'.format(paper_id))
                continue
                #assert(paper.num == paper_id)
            for reviewer in reviewers:
                if reviewers[reviewer].email == reviewer_email:
                    break
            if reviewers[reviewer].email != reviewer_email:
                print('Found a reviewer that is not in users: {}'.format(reviewer_email))
                continue
            for year in reviewers[reviewer].coauthors:
                for author in paper.authors:
                    if author in reviewers[reviewer].coauthors[year]:
                        print('Possible conflict: {} reviewed paper {} but is conflicted with {} in {}'.format(reviewer, paper_id, author, year))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Check reviews for missed conflicts. Run the script with: python3 {} hotcrp-users-mapped.pickle hotcrp-authors.csv hotcrp-scores.csv'.format(sys.argv[0]))
        exit(1)
    # Load reviewer and coauthor information
    reviewers = load_coauthors(sys.argv[1])

    current_year = datetime.now().year
    for reviewer in reviewers:
        print('{} -> {} {} {} {} {} {}'.format(reviewer, len(reviewers[reviewer].coauthors[current_year]), len(reviewers[reviewer].coauthors[current_year-1]), len(reviewers[reviewer].coauthors[current_year-2]), len(reviewers[reviewer].coauthors[current_year-3]), len(reviewers[reviewer].coauthors[current_year-4]), len(reviewers[reviewer].coauthors[current_year-5])))

    papers = get_papers(sys.argv[2])

    check_conflicts(sys.argv[3], papers, reviewers)