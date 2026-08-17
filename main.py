# Copyright 2026 - Seb Johnstone @SebJNZ
import requests, os, caldav, mailer
from datetime import datetime
from icalendar import Calendar
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

load_dotenv()

# Define Constants
ECS_CALENDAR_URL = os.getenv("ECS_CALENDAR_URL")
RADICALE_CALENDAR_URL = os.getenv("RADICALE_CALENDAR_URL") # e.g: http://localhost:5232/user/my-calendar
RADICALE_USERNAME = os.getenv("RADICALE_USERNAME")
RADICALE_PASSWORD = os.getenv("RADICALE_PASSWORD")
COMPARABLE_FIELDS = ["SUMMARY", "URL", "DESCRIPTION"]

TIMEZONE = ZoneInfo("Pacific/Auckland")

# MAILER CONSTANT
USEMAILER = os.getenv("USEMAILER", "False").lower() in ("true")

'''
ECS CALENDAR Formatting
  * SUMMARY -> Returns Course Name, Assignment Name and due date. 
    Format: "{COURSE} - {TASK NAME}  ({DUE_TIME am/pm})" 
  * URL -> Returns submission URL.
    Format: "https://apps.ecs.vuw.ac.nz/submit/{COURSE}/{TASK NAME}"
  * DESCRIPTION -> Returns submission URL and description
    Format: "{URL}{DESCRIPTION}"
  * DTSTART -> Assignment/Test due day (excluding time)
    Format: Type(date)
  * DTEND -> Returns day after due date for some reason (excluding time) ...
    Format: Type(date)
'''

def loadECSCal():
	RESPONSE = requests.get(ECS_CALENDAR_URL)
	RESPONSE.raise_for_status()

	return Calendar.from_ical(RESPONSE.text) # Convert returned text to calendar object

def collectECSUIDs(ecs_calendar):
    uids = []
    for event in ecs_calendar.walk():
        if event.name == "VEVENT":
            uid = event.get('UID')
            if uid:
                uids.append(uid.to_ical().decode('utf-8'))
    return uids

def collectRadicaleUIDs(radicale_calendar):
	uids = []
	for event in radicale_calendar.get_events():
		uid = event.icalendar_component.get("uid")
		if uid:
			uids.append(uid.to_ical().decode('utf-8'))
	return uids

def loadRadicaleCal():
	client = caldav.DAVClient(
		url=RADICALE_CALENDAR_URL,
		username=RADICALE_USERNAME,
		password=RADICALE_PASSWORD
	)

	return caldav.Calendar(client = client, url=RADICALE_CALENDAR_URL)

def getDate(summary, date):
	if "(Due" in summary:
		try:
			timeString = summary.split("(Due ")[-1].rstrip(")")
			timeObject = datetime.strptime(timeString, "%I:%M %p").time()
		except ValueError:
			timeObject = datetime.min.time()
	else:
		timeObject = datetime.min.time()	
	
	if isinstance(date, datetime):
		return datetime.combine(date.date(), timeObject, tzinfo=TIMEZONE)
	date = datetime.strptime(date, "%Y%m%d")
	return datetime.combine(date, timeObject, tzinfo=TIMEZONE)

def walkCalendarData(radicaleCalendar, ecsUIDs, indices, comparableEvents, notificationData):
	# Load Calendars
	ecsCalendar = loadECSCal()
	radicaleUIDs = collectRadicaleUIDs(radicaleCalendar)
    
	for event in ecsCalendar.walk():
		if event.name == "VEVENT":
			uid = event.get('UID').to_ical().decode('utf-8')
			if uid:
				ecsUIDs.append(uid)
				if uid in radicaleUIDs:
					indices.append(uid)
					comparableEvents.append({
						"SUMMARY": event.get("SUMMARY").to_ical().decode('utf-8') if event.get("SUMMARY") else "",
						"URL": event.get("URL").to_ical().decode('utf-8') if event.get("URL") else "",
						"DESCRIPTION": event.get("DESCRIPTION").to_ical().decode('utf-8') if event.get("DESCRIPTION") else "No description provided",
						"START": event.get("DTSTART", "").to_ical().decode('utf-8'),
						"UID": uid
					})
				else:
					url = event.get("URL", "").to_ical().decode('utf-8') if event.get("URL") else ""
					start_str = event.get("DTSTART", "")
     
					if not start_str:
						print("Event does not contain a start, unable to add. UID: " + uid + " URL: " + url)
						continue
     
					summary = event.get("SUMMARY")
					if not summary:
						print("Event does not contain a summary, unable to add. UID: " + uid + " URL: " + url)
						continue
						
					summary_str = summary.to_ical().decode('utf-8')
					description = event.get("DESCRIPTION").to_ical().decode('utf-8') if event.get("DESCRIPTION") else "No description provided"
					
					start_decoded = start_str.to_ical().decode('utf-8')
					exact_due_datetime = getDate(summary_str, start_decoded)
  
					radicaleCalendar.add_event(
						dtstart=exact_due_datetime,
						dtend=exact_due_datetime,
						summary=summary_str,
						description=description,
						url=url,
						uid=uid
					)
     
					notificationData["NEW"].append({
						"SUMMARY": summary_str,
						"DESCRIPTION": description,
						"URL": url,
						"DATE": exact_due_datetime,
						"UID": uid
					})
     
	return radicaleCalendar
 
def clearRadicaleCalendarData(calendar):
    for event in calendar.get_events():
        event.delete()
    
def scanForUpdates(radicaleCalendar, ecsUIDs, indices, comparableEvents, notificationData):
	for event in radicaleCalendar.get_events():
		uid = event.icalendar_component.get("uid").to_ical().decode('utf-8')
		if uid in ecsUIDs:
			if uid in indices:
				ecsData = comparableEvents[indices.index(uid)]
				dtend = event.icalendar_component.get("dtend")
				dtstart = event.icalendar_component.get("dtstart")
    
				if dtend:
					end = dtend.dt
				elif dtstart:
					end = dtstart.dt
				else:
					print(f"Skipping corrupted event (no start or end date): {uid}")
					continue
				
				radicaleData = {
					"SUMMARY": event.icalendar_component.get("summary").to_ical().decode('utf-8'),
					"URL": event.icalendar_component.get("url").to_ical().decode('utf-8') if event.icalendar_component.get("URL") else "",
					"DESCRIPTION": event.icalendar_component.get("description").to_ical().decode('utf-8'),
					"DATE": end
				}

				if radicaleData["DATE"].tzinfo is None:
					radicaleData["DATE"] = radicaleData["DATE"].replace(tzinfo=TIMEZONE)
				else:
					radicaleData["DATE"] = radicaleData["DATE"].astimezone(TIMEZONE)
	
				needsSaving = False

				for field in COMPARABLE_FIELDS:
					radClean = radicaleData[field].replace('\\', '')
					ecsClean = ecsData[field].replace('\\', '')
        
					if radClean != ecsClean:
						print("For ", uid, ": ", radClean, " != ", ecsClean)
						if field in event.icalendar_component:
							event.icalendar_component.pop(field)
					
						event.icalendar_component.add(field, ecsData[field])

						needsSaving = True
      
						if uid in notificationData["UPDATES"]["UID"]:
							index = notificationData["UPDATES"]["UID"].index(uid)
							notificationData["UPDATES"]["NEW_DATA"][index][field] = ecsData[field]
							notificationData["UPDATES"]["OLD_DATA"][index][field] = radicaleData[field]
						else:
							notificationData["UPDATES"]["UID"].append(uid)
							notificationData["UPDATES"]["NEW_DATA"].append({
                                "EVENT_TITLE": ecsData["SUMMARY"],
                                "UID": uid,
                                field: ecsData[field]
                            })
       
							notificationData["UPDATES"]["OLD_DATA"].append({
                                field: radicaleData[field]
                            })
							
		
				ECSdate = getDate(ecsData["SUMMARY"], ecsData["START"])
				ECSdate = ECSdate.replace(tzinfo=TIMEZONE)
	
				if (ECSdate != radicaleData["DATE"]):
					if "DTSTART" in event.icalendar_component:
						event.icalendar_component.pop("DTSTART")
					if "DTEND" in event.icalendar_component:
						event.icalendar_component.pop("DTEND")

					event.icalendar_component.add("DTSTART", ECSdate)
					event.icalendar_component.add("DTEND", ECSdate)
		
					needsSaving = True					

					if uid in notificationData["UPDATES"]["UID"]:
						index = notificationData["UPDATES"]["UID"].index(uid)
						notificationData["UPDATES"]["NEW_DATA"][index]["DATE"] = ECSdate
						notificationData["UPDATES"]["OLD_DATA"][index]["DATE"] = radicaleData["DATE"]
					else:
						notificationData["UPDATES"]["UID"].append(uid)
      
						notificationData["UPDATES"]["NEW_DATA"].append({
                            "EVENT_TITLE": ecsData["SUMMARY"],
                            "UID": uid,
                            "DATE": ECSdate
                        })
      
						notificationData["UPDATES"]["OLD_DATA"].append({
                            "DATE": radicaleData["DATE"]
                        })
	
				if needsSaving:
					event.save()
		else:
			print("Removing Event: ", uid)
			event.delete()

def main():
	radicaleCalendar = loadRadicaleCal()
	ecsUIDs = []
	indices = []
	comparableEvents = []
	notificationData = {
		"NEW": [],
		"UPDATES": {
			"UID": [],
			"NEW_DATA": [],
			"OLD_DATA": []
		}
	}

	#clearRadicaleCalendarData(radicaleCalendar)
	radicaleCalendar = walkCalendarData(radicaleCalendar, ecsUIDs, indices, comparableEvents, notificationData)
	scanForUpdates(radicaleCalendar, ecsUIDs, indices, comparableEvents, notificationData) # Scans and fixes data
	if USEMAILER:
		if notificationData["NEW"] or notificationData["UPDATES"]["UID"]:
			mailer.emailer(notificationData)
 
if __name__ == "__main__":
	main()