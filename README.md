# Inquisitor: check for missed conflicts

This set of scripts allows a PC chair or administrator to check for missed conflicts in a HotCRP instance.

Setup: download [dblp.xml.gz](https://dblp.uni-trier.de/xml/dblp.xml.gz) and [dblp.dtd](https://dblp.uni-trier.de/xml/dblp.dtd) from dblp.

## Step 1: Matching reviewers

This script allows you to match your reviewers to DBLP authors. Go to your HotCRP instance, select "Users" and select "PC Committee", then scroll to the bottom and select all people to download "Names and emails". This should give you the file `hotcrp-users.csv`.

Run the matching `python3 match_reviewers_dblp.py hotcrp-users.csv`.

Double check the file `hotcrp-users-matched.csv` and ensure for any reviewer with multiple author matches that the first match is the correct one; you can leave the remaining ones.

The format is `HotCRP name, email, ORCID, DBLP name`.


## Step 2: Finding coauthors of reviewers

This script finds all coauthors of our reviewers of the current and last 5 years. The result is a pickled file with all the necessary information.

Run the script `python3 find_coauthors.py hotcrp-users-mapped.csv`.


## Step 3: Find any missed conflicts

Now download the juicy data from HotCRP. Go to the submissions page, scroll to the bottom, and "select all papers". Download two files `Review/Scores (CSV)` resulting in the file `hotcrp-scores.csv` and `Paper Information/Authors (CSV)` resulting in the file `hotcrp-authors.csv`.

Run the script `python3 check_reviews.py hotcrp-users-mapped.pickle hotcrp-authors.csv hotcrp-scores.csv` and check the reported results in HotCRP or through the log files.