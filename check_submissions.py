#!/usr/bin/python3
'''
The goal of this script is to quickly match number of submissions and authors
'''
import csv
import sys

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
    if len(sys.argv) == 1:
        print('Check author data for total number of submissions. Run the script with: python3 {} hotcrp-authors.csv [hotcrp-author2.csv ...]'.format(sys.argv[0]))
        exit(1)

    authors = {}
    for i in range(len(sys.argv)-1):
        print(sys.argv[i+1])
        with open(sys.argv[i+1], 'r') as f:
            authors_csv = csv.reader(f)
            for row in authors_csv:
                if row[0] == 'paper':
                    continue
                reviewer = row[2]+' '+row[3]+' <'+row[4]+'>'
                if reviewer in authors:
                    authors[reviewer] += 1
                else:
                    authors[reviewer] = 1
    sorted_authors = sorted(authors.items(), key=lambda kv: (kv[1], kv[0]))
    for pair in sorted_authors:
        print(pair)
