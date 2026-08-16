# VUW Calendar Sync
Want to be **up-to-date** and have **full transparency** with changes on **assignment due dates**, **test times**, **lecture times**, while still retaining full uptime if VUWs servers go down? Look no further than VUW Calendar Sync.

# Setup
You can either run it manually or automate it, either way you will need to follow these steps.

## Prerequisites:
Python3 and pip

Radicale Server

An internet connection

ECS Calendar URL (which you can copy from [here](https://apps.ecs.vuw.ac.nz/apps/assessment_calendar/) > Add to external calendar)

## Steps
1. Install requirements:

`pip3 install -r requirements.txt`

2. Create `.env` file, with the following parameters (change values of course):

```
ECS_CALENDAR_URL = "https://YOUR_CALENDAR_URL_FROM_ECS.ac.nz/"
RADICALE_CALENDAR_URL = "https://yourcalendar.com/"
RADICALE_USERNAME = "admin"
RADICALE_PASSWORD = "password1234"
```

3. Run the program:

`python3 main.py`

# Support
Currently VUW Calendar Sync only supports the ECS calendar.

In the future we will support [timetable.victoria.ac.nz](https://timetable.victoria.ac.nz/)'s calendar for lecture, tutorial and lab times.

