# Copyright 2026 - Seb Johnstone @SebJNZ
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv

load_dotenv()

def emailer(notificationData):
    email = MIMEMultipart("alternative")
    email["From"] = formataddr((os.getenv("EMAIL_DSPNAME"), os.getenv("SMTP_EMAIL_ADDRESS")))
    email["To"] = os.getenv("RECIEVER_EMAIL")
    if os.getenv('EMAIL_SUBJECT_PREPEND'):
        email["Subject"] = f"{os.getenv('EMAIL_SUBJECT_PREPEND')} - VUW Calendar Update"
    else:
        email["Subject"] = "VUW Calendar Update"
    
    new_html = ""
    new_text = ""
    new_event = False
    if notificationData["NEW"]:
        new_event = True
        
        for event in notificationData["NEW"]:
            raw_date = event["DATE"]
            clean_date = raw_date.strftime("%b %d, %I:%M %p")
            
            html_draft = f"""            <div class="event-card">
    <p class="event-title">{event['SUMMARY']}</p>
        
    <p class="change-label">Description</p>
    <p class="change-data">
        <span class="new-data">{event['DESCRIPTION']}</span>
    </p>

    <p class="change-label">URL</p>
    <p class="change-data">
        <span class="new-data"><a href="{event['URL']}">{event['URL']}</a></span>
    </p>

    <p class="change-label">Date</p>
    <p class="change-data">
        <span class="new-data">{clean_date}</span>
    </p>

    <p class="change-label">UID</p>
    <p class="change-data">
        <span class="new-data">{event['UID']}</span>
    </p>
</div>

"""
            new_html += html_draft
            
            text_draft = f"""
==================================================
NEW EVENT:   {event['SUMMARY']}
==================================================
DESCRIPTION: {event['DESCRIPTION']}
URL:         {event['URL']}
DATE:        {clean_date}
UID:         {event['UID']}

"""
            new_text += text_draft
    
    updated_html = ""
    updated_text = ""
    updated_event = False
    if notificationData["UPDATES"]["UID"]:
        updated_event = True
        for event in notificationData["UPDATES"]["UID"]:
            index = notificationData["UPDATES"]["UID"].index(event)
            new_data = notificationData["UPDATES"]["NEW_DATA"][index]
            old_data = notificationData["UPDATES"]["OLD_DATA"][index]
            
            html_draft = f"""<div class="event-card">
    <p class="event-title">{new_data['EVENT_TITLE']}</p>
    
"""
            text_draft = f"""
==================================================
UPDATED EVENT: {new_data['EVENT_TITLE']}
==================================================
"""

            for feature, old_value in old_data.items():
                new_value = new_data[feature]
                
                if feature == "DATE":
                    old_str = old_value.strftime("%b %d, %-I:%M %p")
                    new_str = new_value.strftime("%b %d, %-I:%M %p")
                else:
                    old_str = str(old_value)
                    new_str = str(new_value)
                
                html_draft += f"""
    
    <p class="change-label">{feature} Changed</p>
    
    <p class="change-data">
        <span class="old-data">{old_str}</span>
        &rarr; 
        <span class="new-data">{new_str}</span>
    </p>
"""             
                text_draft += f"{feature}:\nOLD: {old_str}\nNEW: {new_str}\n\n"
                
            html_draft += """\n</div>\n"""

            updated_html += html_draft
            updated_text += text_draft
            
    deleted_html = ""
    deleted_text = ""
    deleted_event = False
    if notificationData["REMOVED"]:
        deleted_event = True
        
        for event in notificationData["REMOVED"]:
            html_draft = f"""<div class="event-card">
    <p class="event-title">{event["TITLE"]}</p>
    
"""
            text_draft = f"""
==================================================
DELETED EVENT: {event["TITLE"]}
==================================================
"""
            for features in event["DATA"]:
                for feature, value in features.items():                  
                    html_draft += f"""
    <p class="change-label">{feature}</p>
    <p class="change-data">
        <span class="old-data">{value}</span>
    </p>
"""
                    text_draft += f"{feature}: {value}\n"
                
            html_draft += """\n</div>\n"""
            text_draft += "\n"
            deleted_html += html_draft
            deleted_text += text_draft
            
    text = """Hi,
There have been some calendar updates.

"""
    
    html = f"""<html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
                color: #333;
                line-height: 1.5;
            }}
            a {{
                color: #005A9C !important;
                text-decoration: none !important;
            }}
            .event-card {{
                background-color: #f8f9fa;
                border-left: 4px solid #005A9C;
                padding: 12px 16px;
                margin-bottom: 16px;
                border-radius: 0 4px 4px 0;
            }}
            .event-title {{
                font-weight: bold;
                font-size: 1.05em;
                margin: 0 0 8px 0;
                color: #111;
            }}
            .change-label {{
                font-size: 0.85em;
                text-transform: uppercase;
                color: #666;
                letter-spacing: 0.5px;
                margin: 0;
            }}
            .change-data {{
                margin: 2px 0 12px 0;
                font-size: 0.95em;
            }}
            .old-data {{ color: #888; text-decoration: line-through; }}
            .new-data {{ color: #2ea043; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <p>Hi,</p>
            <p>There have been some calendar updates.</p>
"""

    if new_event:
        html += f"""            <h4 style="margin: 24px 0 12px 0; border-bottom: 1px solid #eee; padding-bottom: 8px;">
                New Events
            </h4>
{new_html}
"""
        text += f"""New Events:
{new_text}
"""
    
    if updated_event:
        html += f"""            <h4 style="margin: 24px 0 12px 0; border-bottom: 1px solid #eee; padding-bottom: 8px;">
                Updated Events
            </h4>
{updated_html}
"""
        text += f"""Updated Events:
{updated_text}
"""

    if deleted_event:
        html += f"""            <h4 style="margin: 24px 0 12px 0; border-bottom: 1px solid #eee; padding-bottom: 8px;">
                Deleted Events
            </h4>
{deleted_html}        
"""
        text += f"""Deleted Events:
{deleted_text}
"""
        

    html += """            <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0 15px 0;">
            <p style="color:#888; font-size: 0.85em; text-align: center;">
                This is an automated notification from your <a href="https://github.com/SebJNZ/VUW-Calendar-Sync">VUW Calendar Sync</a> instance.
            </p>
        </div>
    </body>
</html>"""

    text += "This is an automated notification from your VUW Calendar Sync instance."
    
    text_body = MIMEText(text, 'plain')
    html_body = MIMEText(html, 'html')

    email.attach(text_body)
    email.attach(html_body)

    with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT")) as s:
        s.login(os.getenv("SMTP_EMAIL_ADDRESS"), os.getenv("SMTP_EMAIL_PASSWORD"))
        s.send_message(email)