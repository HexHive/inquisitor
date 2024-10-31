#!/usr/bin/python3
'''
The goal of this script is to validate reviewer bidding
'''
import csv
import sys

class Reviewer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.positive_bids = 0
        self.negpos_bids = 0
        self.bids = {}
    
    def add_bid(self, paper_authors, preference, topic_score):
        if preference > 0:
            # positive bids
            self.positive_bids += 1
            for author in paper_authors:
                if author in self.bids:
                    self.bids[author] += 1
                else:
                    self.bids[author] = 1
        if topic_score < 0 and preference > 0:
            # topic score says nay but preference says yay
            self.negpos_bids += 1
    
    def report(self):
        resp = ''
        for author in self.bids:
            if self.bids[author] >= self.positive_bids*0.20:
                resp += '- {} of the positive bids went to {}\n'.format(self.bids[author], author)
            if self.bids[author] >= 3:
                resp += '- {} of the positive bids went to {}\n'.format(self.bids[author], author)
        if len(resp) != 0:
            print('Reviewer {} <{}> has {} positive bids and {} positive bids with negative topic score'.format(self.name, self.email, self.positive_bids, self.negpos_bids))
            print(resp[:-1])


def read_papers(papers_csv):
    with open(papers_csv, 'r') as f:
        papers_csv = csv.reader(f)
        paper_id = 0
        paper_authors = {}
        authors = []
        for row in papers_csv:
            if row[0] == 'paper':
                # validate data format
                assert(row[1] == 'title' and row[2] == 'first' and row[3] == 'last' and row[4] == 'email')
                continue
            if paper_id != row[0]:
                if paper_id != 0:
                    # add one set of authors/paper
                    paper_authors[paper_id] = authors
                    authors = []
                paper_id = int(row[0])
            authors.append('{} {} <{}>'.format(row[2], row[3], row[4]))
        # add last authors to set
        paper_authors[paper_id] = authors
    return paper_authors

def read_prefs(allprefs_csv, paper_authors):
    with open(allprefs_csv, 'r') as f:
        allprefs_csv = csv.reader(f)
        reviewers = {}
        for row in allprefs_csv:
            if row[0] == 'paper':
                # validate data format
                assert(row[2] == 'given_name' and row[3] == 'family_name' and row[4] == 'email' and row[6] == 'preference' and row[7] == 'topic_score')
                continue
            name = '{} {}'.format(row[2], row[3])
            email = row[4]
            if not email in reviewers:
                reviewers[email] = Reviewer(name, email)
            preference = int(row[6]) if row[6] != '' else 0
            topic_score = int(row[7]) if row[7] != '' else 0
            reviewers[email].add_bid(paper_authors[int(row[0])], preference, topic_score)
    return reviewers



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Check allpref data for bidding outliers. Run the script with: python3 {} hotcrp-authors.csv hotcrp-allprefs.csv'.format(sys.argv[0]))
        exit(1)

    paper_authors = read_papers(sys.argv[1])
    reviewers = read_prefs(sys.argv[2], paper_authors)

    for reviewer in sorted(reviewers):
        reviewers[reviewer].report()
