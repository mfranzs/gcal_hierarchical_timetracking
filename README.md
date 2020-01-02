Status: Personal script. Ugly code, but usable. PRs very welcome, if you want.

# Google Calendar Hierarchical Time Tracker
A time-tracking productivity script that pulls from Google Calendar. Define task categories (and corresponding keywords) to match with gcal events. 

Breaks down tasks hierarchically, helping you see time spent in different categories as a whole. Reports time distribution through text, or visually.

## Installation
1. pip3 install -r requirements.txt
2. Setup your google calendar API credentials. follow: https://developers.google.com/calendar/quickstart/python
3. Make a params.py, copy from example_params.py and change as you like. 

## Run python scrape.py

Options:
- python scrape.py today OR python scrape.py t
- python scrape.py yesterday OR python scrape.py y
- python scrape.py month OR python scrape.py m
- python scrape.py (DEFAULT IS WEEK)
- python scrape.py "02/11/2018" "02/18/2018"