import datetime
from dateutil import parser
import sys


def parseTimeRange():
    if len(sys.argv) == 3:
        TIME_MIN = (parser.parse(sys.argv[1]) +
                    datetime.timedelta(days=0, hours=5))
        TIME_MAX = (parser.parse(sys.argv[2]) +
                    datetime.timedelta(days=0, hours=5))
    else:
        FORWARD_DAYS_OFFSET = 0
        DAYS_OFFSET = -6
        FORWARD_DAYS_OFFSET = 1
        if len(sys.argv) == 2:
            if sys.argv[1] == "yesterday" or sys.argv[1] == "y":
                DAYS_OFFSET = -1
                FORWARD_DAYS_OFFSET = 0
            elif sys.argv[1] == "today" or sys.argv[1] == "t":
                DAYS_OFFSET = 0
                FORWARD_DAYS_OFFSET = 1
            elif sys.argv[1] == "month" or sys.argv[1] == "m":
                DAYS_OFFSET = -31
            elif sys.argv[1] == "year" or sys.argv[1] == "yr":
                DAYS_OFFSET = -365

        TIME_MIN = (datetime.datetime.fromordinal(datetime.date.today().toordinal(
        )) + datetime.timedelta(days=DAYS_OFFSET, hours=5))
        TIME_MAX = (datetime.datetime.fromordinal(datetime.date.today().toordinal(
        )) + datetime.timedelta(days=FORWARD_DAYS_OFFSET, hours=5))

    timeMinString = TIME_MIN.isoformat() + 'Z'
    timeMaxString = TIME_MAX.isoformat() + 'Z'

    return TIME_MIN, TIME_MAX, timeMinString, timeMaxString
