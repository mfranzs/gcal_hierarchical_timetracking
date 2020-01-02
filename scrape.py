from __future__ import print_function
import os
import sys

import collections
import pytz
import time
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import timedelta, tzinfo
import pytz

try:
    from params import CALENDARS_TO_SCRAPE, categories, categories_to_color
except ModuleNotFoundError as e:
    print("Error: You must copy example_params.py to params.py and customize it.")
    quit()

import cv2
import numpy as np

import util
from util import color

def main(write=print):
    TIME_MIN, TIME_MAX, timeMinString, timeMaxString = util.parseTimeRange()
    timezone = pytz.timezone("America/New_York")
    TIME_MIN = timezone.localize(TIME_MIN)
    TIME_MAX = timezone.localize(TIME_MAX)

    print("Time range", TIME_MIN, TIME_MAX)

    def colorText(colorName, text):
        if write == print:
            return f"{color[colorName]}{text}{color['END']}"
        else:
            return f"<span style='color: {colorName}'>{text}</span>"

    def boldText(text):
        if write == print:
            return colorText("BOLD", text)
        else:
            return f"<b>{text}</b>"

    def allCategories(categoriesSubTree=categories):
        for c in categoriesSubTree:
            if isinstance(categoriesSubTree[c], list):
                yield c, [c] + categoriesSubTree[c]
            else:
                for subData in allCategories(categoriesSubTree[c]):
                    yield subData

    category_to_parent = {}
    seen_categories = set()
    def fillOutCategoryToParent(categoriesSubTree, subTreeName=None):
        for k in categoriesSubTree.keys():
            category_to_parent[k] = subTreeName

            if k in seen_categories:
                quit("Sorry, each category must have a unique name." + k)
            seen_categories.add(k)

            if isinstance(categoriesSubTree[k], dict):
                fillOutCategoryToParent(categoriesSubTree[k], k)

    fillOutCategoryToParent(categories)

    def getCategory(summary):
        def distance(summary, trigger):
            return -len(trigger) # For now, just favor longer triggers
        
        if summary is not None:
            closestCategory = None
            closestTriggerDistance = 99999

            for c, triggers in allCategories():
                for trigger in triggers: 
                    if trigger.lower() in summary.lower():
                        if distance(summary, trigger) < closestTriggerDistance:
                            closestCategory = c
                            closestTriggerDistance = distance(summary, trigger)
            if closestCategory is not None:
                return closestCategory

        return "UNKNOWN"

    def getCategoryColor(category):
        if category in categories_to_color:
            return categories_to_color[category]
        elif category in category_to_parent:
            return getCategoryColor(category_to_parent[category])
        else:
            return (100, 100, 100)

    def subtreeTotalTime(categoriesSubTree):
        t = 0
        for c in categoriesSubTree:
            if isinstance(categoriesSubTree[c], list):
                t += time[c]
            else:
                t += subtreeTotalTime(categoriesSubTree[c])
        return t

    def percent(a, b):
        return colorText("DARKCYAN", "("+str(int(100 * a / b))+"%)")

    def combineEvents(eventsInACategory):
        combinedEvents = collections.defaultdict(lambda: 0)
        for event in eventsInACategory:
            combinedEvents[event[0]] += event[1]
        return [i for i in reversed(sorted([(k, combinedEvents[k]) for k in combinedEvents], key=lambda x: x[1]))]


    def printTree(printEvents, hideEmptyLabels, categoriesSubTree=categories, depth = 0, totalTime = None):
        if not totalTime:
            totalTime = sum(time[c] for c in time)

        for c in categoriesSubTree:
            isLeaf = isinstance(categoriesSubTree[c], list)
            if isLeaf:
                t = time[c]
            else:
                t =  subtreeTotalTime(categoriesSubTree[c])

            if t > 0 or not hideEmptyLabels:
                eventLabels = (combineEvents(timeAssignments.get(
                    c, "")) if printEvents and isLeaf else "")
                write("\t"*depth, colorText("YELLOW", c),  "\t", t,  percent(t, totalTime), "\t" * \
                    (4 - depth), eventLabels)

            if not isinstance(categoriesSubTree[c], list):
                printTree(
                    printEvents, hideEmptyLabels, categoriesSubTree[c], depth + 1, totalTime)

    def printUnknownEvents():
        if len(timeAssignments["UNKNOWN"]) > 0:
            totalUnkownTime = sum(e[1] for e in timeAssignments["UNKNOWN"])
            write("\n Warning: There were some unknown events which didn't fit in any category, summing to %s total hours" % totalUnkownTime)
        for event in timeAssignments["UNKNOWN"]:
            write("\t", boldText(event[0]),"(",event[1],")")

    time = {}
    timeAssignments = {}
    for c, triggers in allCategories():
        if c in time:
            raise Exception("This is poorly written, so doesn't support categories with the same name", c)
        time[c] = 0
        timeAssignments[c] = []

    # Setup visualization
    num_days = (TIME_MAX - TIME_MIN).days
    SECONDS_PER_HOUR = 3600
    HOURS_PER_DAY = 24
    VERTICAL_BLOCK_SIZE = (2 if num_days > 60 else 20) if num_days > 7 else 40
    HORIZONTAL_BLOCK_SIZE = 19 # Each 15 min block
    DISPLAY_TEXT = VERTICAL_BLOCK_SIZE >= 20
    
    # Initialize blank visualization to grey
    visualization = np.ones(
        (num_days * VERTICAL_BLOCK_SIZE, HOURS_PER_DAY * HORIZONTAL_BLOCK_SIZE * 4, 3), dtype=np.uint8) * 200

    # Scraping
    print("Fetch all events")
    for event in util.allEvents(CALENDARS_TO_SCRAPE, timeMinString, timeMaxString):            
        if 'dateTime' not in event['start']:
            # skip all-day events
            continue 

        start = max(parser.parse(event['start']['dateTime']), TIME_MIN.replace(tzinfo=pytz.UTC))
        end = min(parser.parse(event['end']['dateTime']), TIME_MAX.replace(tzinfo=pytz.UTC))
        eventLen =  (end - start).seconds / 60. / 60

        # Categorize
        cat = getCategory(event.get("summary"))

        # Aggregate
        time[cat] += eventLen
        timeAssignments[cat].append((event.get("summary"), eventLen))

        # Visualize
        # TODO: Remove +5 hack to get timezone offset
        fifteen_min_block = start + timedelta(hours = 5) 
        blockIndex = 0
        while fifteen_min_block < end + timedelta(hours = 5):
            fifteen_min_block += timedelta(minutes = 15)

            day_offset = (fifteen_min_block - TIME_MIN).days
            hour_offset = (fifteen_min_block - TIME_MIN).seconds / 3600 % HOURS_PER_DAY

            c = getCategoryColor(cat)

            cv2.rectangle(visualization, 
                (int(hour_offset * HORIZONTAL_BLOCK_SIZE * 4), day_offset *VERTICAL_BLOCK_SIZE), 
                (int(hour_offset * HORIZONTAL_BLOCK_SIZE * 4) + HORIZONTAL_BLOCK_SIZE, day_offset * VERTICAL_BLOCK_SIZE + VERTICAL_BLOCK_SIZE), 
                c,
                -1)

            if blockIndex == 0:
                cv2.rectangle(visualization,
                              (int(hour_offset * HORIZONTAL_BLOCK_SIZE * 4),
                               day_offset * VERTICAL_BLOCK_SIZE),
                              (int(hour_offset * HORIZONTAL_BLOCK_SIZE * 4),
                                  day_offset * VERTICAL_BLOCK_SIZE + VERTICAL_BLOCK_SIZE),
                              color = 0)

            if blockIndex * 2 < len(cat) and DISPLAY_TEXT:
                cv2.putText(
                    visualization, 
                    cat[blockIndex * 2: blockIndex * 2 + 2],
                    (int(hour_offset * HORIZONTAL_BLOCK_SIZE * 4), day_offset * VERTICAL_BLOCK_SIZE + 13),
                    cv2.FONT_HERSHEY_PLAIN,
                    fontScale=.9,
                    color=0 if sum(c) / 3 > 50 else (128, 128, 128),
                    thickness=1)
            blockIndex += 1

    # Draw lines between days
    for day_offset in range(num_days):
        cv2.rectangle(visualization,
            (0, day_offset * VERTICAL_BLOCK_SIZE),
            (HOURS_PER_DAY * HORIZONTAL_BLOCK_SIZE * 4, day_offset * VERTICAL_BLOCK_SIZE),
            color=0)

    write("=====")
    write("Total time:", sum(time[c] for c in time)/24, "days")
    write("=====")

    printTree(True, False)

    write("=====")
    write("Total time:", sum(time[c] for c in time)/24, "days")
    write("=====")

    printTree(True, True)

    write("=====")
    write("Total time:", sum(time[c] for c in time)/24, "days")
    write("=====")

    printTree(False, True)

    printUnknownEvents()

    write("(data between", TIME_MIN, TIME_MAX, ")")

    while True:
        cv2.imshow('visualization', visualization)
        key = cv2.waitKey(0)  
        if chr(key) == 'q':
            break

if __name__ == '__main__':
    main()
