from __future__ import print_function
import httplib2
from apiclient import discovery
import os
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
from .color import color

print("Loading services")

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Time Tracking'

# Setup the Calendar API
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()), cache_discovery=False)

print("Loaded services!")

def allEvents(CALENDARS_TO_SCRAPE, timeMinString, timeMaxString):
    CALENDARS_TO_SCRAPE_USED = set()
    for cal in service.calendarList().list().execute().get('items', []):
        if cal.get("summary") in CALENDARS_TO_SCRAPE:
            CALENDARS_TO_SCRAPE_USED.add(cal.get("summary"))
            pageToken = ""
            while pageToken is not None:
                eventsResult = service.events().list(
                    calendarId=cal.get("id"), timeMin=timeMinString, timeMax=timeMaxString, singleEvents=True,
                    orderBy='startTime', pageToken=pageToken).execute()
                pageToken = eventsResult.get('nextPageToken', None)
                for event in eventsResult.get('items', []):
                    yield event
    for cal in CALENDARS_TO_SCRAPE:
        if cal not in CALENDARS_TO_SCRAPE_USED:
            quit("Error: Didn't find calendar %s%s%s, but that calendar was requested in the CALENDARS_TO_SCRAPE setting" % (
                color.BOLD, cal, color.END))
