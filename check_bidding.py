#!/usr/bin/python3
'''
The goal of this script is to validate reviewer bidding
'''
import csv
import sys

POSITIVE_BID_MIN = 0.05 # we expect positive bids to at least % papers
POSITIVE_AUTHOR_BIDS_RATIO_THRESHOLD = 0.20 # threshold of percentage of positive bids to a single author above which it becomes suspicious
POSITIVE_AUTHOR_BIDS_THRESHOLD = 4 # report if more than X positive bids for the same author
BAI_MAX_POSITIVE_BIDS = 20 # to positive bids to evaluate, use -1 to check all
BAI_MIN_POSITIVE_SCORE = 5 # minimum positive score to count

class Reviewer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.positive_bids = 0
        self.negpos_bids = 0
        self.bids = {} # map with author -> array of positive preferences
        self.preferences = [] # array with all positive preferences
    
    def add_bid(self, paper_authors, preference, topic_score):
        if preference > 0:
            # positive bids
            self.positive_bids += 1
            for author in paper_authors:
                if author in self.bids:
                    self.bids[author].append(preference)
                else:
                    self.bids[author] = [preference]
            self.preferences.append(preference)
        if topic_score < 0 and preference > 0:
            # topic score says nay but preference says yay
            self.negpos_bids += 1
    
    def report(self, nr_papers, papers_per_author):
        resp = ''
        # check ratio of positive bids
        if self.positive_bids <= nr_papers*POSITIVE_BID_MIN:
            resp += '- only {:.2f}% of bids were positive out of {} papers!\n'.format(self.positive_bids/float(nr_papers)*100, nr_papers)

        # check general statistics (if a single author received more than a percentage of positive bids)
        for author in self.bids:
            if len(self.bids[author]) >= self.positive_bids*POSITIVE_AUTHOR_BIDS_RATIO_THRESHOLD:
                resp += '- {} of the positive bids went to {} ({})\n'.format(len(self.bids[author]), author, self.bids[author])
            else: # make sure to only add each author once
                if len(self.bids[author]) >= POSITIVE_AUTHOR_BIDS_THRESHOLD:
                    resp += '- {} of the positive bids went to {} ({})\n'.format(len(self.bids[author]), author, self.bids[author])

        pos_bids = sorted(self.preferences, reverse=True)
        # calcualte min bid based on index max(pos_bids[20], 5)
        min_bid = max(pos_bids[BAI_MAX_POSITIVE_BIDS], BAI_MIN_POSITIVE_SCORE) if len(pos_bids) > BAI_MAX_POSITIVE_BIDS else BAI_MIN_POSITIVE_SCORE
        sampled_pos_bids = [i for i in pos_bids if i >= min_bid]
        if len(sampled_pos_bids) == 0:
            resp += '- no positive bids remaining for BAI\n'
        else:
            BX = sum(sampled_pos_bids)
            for author in self.bids:
                pos_author_bids = [i for i in self.bids[author] if i >= sampled_pos_bids[-1]]
                if len(pos_author_bids) == 0:
                    continue
                BXY = sum(pos_author_bids)
                BAI = (float(BXY)/len(pos_author_bids))/(float(BX)/len(sampled_pos_bids))
                #BAI = (float(BXY)/float(BX))/(papers_per_author[author]/float(nr_papers))
                if BAI > 2.0:
                    resp += '- bidding affinity is high for {}: {:.2f} {} BXY {} BX {} author papers {}\n'.format(author, BAI, pos_author_bids, BXY, BX, papers_per_author[author])
        if len(resp) != 0:
            print('Reviewer {} <{}> has {} positive bids and {} positive bids with negative topic score'.format(self.name, self.email, self.positive_bids, self.negpos_bids))
            print(resp[:-1])


def read_papers(papers_csv):
    with open(papers_csv, 'r') as f:
        papers_csv = csv.reader(f)
        paper_id = '0'
        paper_authors = {}
        authors = []
        papers_per_author = {}
        for row in papers_csv:
            if row[0] == 'paper':
                # validate data format
                assert(row[1] == 'title' and row[2] == 'first' and row[3] == 'last' and row[4] == 'email')
                continue
            if paper_id != row[0]:
                if paper_id != '0':
                    # add one set of authors/paper
                    paper_authors[paper_id] = authors
                    authors = []
                paper_id = row[0]
            author = '{} {} <{}>'.format(row[2], row[3], row[4])
            authors.append(author)
            if author in papers_per_author:
                papers_per_author[author] += 1
            else:
                papers_per_author[author] = 1
        # add last authors to set
        paper_authors[paper_id] = authors
    return paper_authors, papers_per_author

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
            reviewers[email].add_bid(paper_authors[row[0]], preference, topic_score)
    return reviewers



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Check allpref data for bidding outliers. Run the script with: python3 {} hotcrp-authors.csv hotcrp-allprefs.csv'.format(sys.argv[0]))
        exit(1)

    paper_authors, papers_per_author = read_papers(sys.argv[1])
    reviewers = read_prefs(sys.argv[2], paper_authors)

    for reviewer in sorted(reviewers):
        reviewers[reviewer].report(len(paper_authors), papers_per_author)
