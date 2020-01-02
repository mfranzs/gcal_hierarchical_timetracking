# Example parameters. 
# * COPY THIS TO params.py TO USE * 


CALENDARS_TO_SCRAPE = [
    "mfranzs123@gmail.com",
]

# Time is broken down hierarchically. A tree is defined below.
# Each item is either:
# - A dictionary of sub-tasks
#   (ex. "Working" has sub-tasks" "Classes", "Learning", "Thinking", etc.)
# - A specific task, represented by a list of alterntaive names for that task 
#   (ex. "Research" is represented in my calendar either by "Research", "Lab Meeting", or "Advisor Meeting")

categories = {
    "Sleeping": {
        "Prep to sleep": ["brush teeth"],
        "Sleep": ["nap", "wake up", "wakeup"],
    },
    "Working": {
        "Classes": {
            "6.006": [],
            "6.881": [],
        },
        "Learning": {
            "Queue": [],
        },
        "Thinking": [],
        "Research": ["Lab Meeting", "Advisor Meeting"],
        "Projects": {
          "Build Time Tracking Project": [],
        },
        "Family": {
        }
    },
    "Sick": {},
    "Homeostasis": {
        "Exercise/Shower": ["Run", "Elliptical", "Shower", "Exercise"],
        "Write": ["Writing", "Journal"],
        "Biking": []
    },
    "Overhead": {
        "Email": [],
        "Organize": ["Work through todo list"],
        "Trash": ["clean up"],
        "Walking": ["walk", "get to", "get home"],
        "Laundry": ["Clean room"],
        "Flying": ["Pack",],
    },
    "Break": {
        "Healthy": {
            "Eating": {
                "Lunch": [],
                "Dinner": [],
            },
            "Consumption": {
                "Movie": []
            },
            "Socializing": {
                "Talking": [],
            },
        },
        "Unhealthy": {
            "Internet": {
                "Waste Time": ["waste", "break"],
                "Relax": [],
                "Web Forums": ["Reddit", "Hacker News"],
            },
            "Video Games": ["Smash"],
        },
        "Vacation": {
            "Travel": ["Flight", "Train", "Your Itinerary", "Airport"],
        },
    },
    "UNKNOWN": ["?"],
}


categories_to_color = {
    # These keys are the unique names in the hierarchy below. Deeper has precedence
    "Sleeping": (0, 0, 0),  # Black

    "Overhead": (0, 0, 255),  # Red
    "Walking": (50, 0, 255),  # Red
    "Organize": (100, 0, 255),  # Red

    "Break": (255, 0, 0),  # Blue
    "Socializing": (255, 255, 0),
    "Dinner": (255, 170, 0),
    "Lunch": (255, 170, 0),
    "Waste Time": (255, 100, 0),
    "Relax": (255, 50, 50),

    "Working": (0, 255, 0),  # Green
    "Classes": (0, 255, 50),  #
    "Project": (0, 255, 125),  #
    "Research": (0, 255, 180),  #
    "Studying": (50, 255, 180),  #
}
