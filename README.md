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
### 0. Create/Enter ENV (optional)
<ins>Create ENV:</ins> `python3 -m venv env`

<ins>Enter ENV:</ins>

**Linux/Mac**:
`source env/bin/activate`

**Windows**:

*CMD*:
`env\Scripts\activate.bat`

*PowerShell*:
`.\env\Scripts\Activate.ps1`



### 1. Install requirements:

`pip3 install -r requirements.txt`


### 2. Create `.env` file, with the following parameters (change values of course):

```
ECS_CALENDAR_URL = "https://YOUR_CALENDAR_URL_FROM_ECS.ac.nz/"
RADICALE_CALENDAR_URL = "https://yourcalendar.com/"
RADICALE_USERNAME = "admin"
RADICALE_PASSWORD = "password1234"
USEMAILER = false

# If using mailer (replace the above USEMAILER with true)
EMAIL_DSPNAME = "VUW Calendar Sync"
SMTP_EMAIL_ADDRESS = "sender@calendar.com"
SMTP_EMAIL_PASSWORD = "supersecretpassword"
SMTP_SERVER = "smtp.calendar.com"
SMTP_PORT = 465
RECIEVER_EMAIL = "reciever@email.com"

# This is optional for mailer (e.g. if equals to "ECS", subject will be: "ECS - VUW Calendar Update")
EMAIL_SUBJECT_PREPEND = ""
```

### 2.5 Mailer Setup (optional)
If you want to receive emails about changes:

* Ensure you have added your mailer details to the .env file (as seen above)
* Ensure you have changed `USEMAILER` to true in .env (as seen above we have it set to false)

### 3. Run the program:

`python3 main.py`

# Run the script on a schedule
To run the script automatically, you will need some form of scheduler. On Linux, you can use a crontab. Example crontab for 7am everyday (using the ENV):

`0 7 * * * /home/user/calendar-syncer/env/bin/python3 /home/user/calendar-syncer/main.py`

# Support
Currently VUW Calendar Sync only supports the ECS calendar.

In the future we will support [timetable.victoria.ac.nz](https://timetable.victoria.ac.nz/)'s calendar for lecture, tutorial and lab times.

