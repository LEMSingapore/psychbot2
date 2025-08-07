# src/calendar_utils.py
# Google Calendar integration utilities for PsychBot appointment booking
# Handles creating therapy session appointments directly in Dr. Sarah Tan's Google Calendar (weddingvowsmanifesto@gmail.com)

# Google API client libraries for Calendar integration
from googleapiclient.discovery import build  # Main Google API client builder
from google.oauth2 import service_account  # Service account authentication (server-to-server)
from datetime import timedelta  # For calculating appointment end times

# ===============================
# CONFIGURATION CONSTANTS
# ===============================

# Google Calendar API permissions - allows full calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Path to the service account credentials file (contains private keys)
# This file allows the application to authenticate with Google Calendar without user login
SERVICE_ACCOUNT_FILE = 'credentials.json'

# The specific Google Calendar ID where appointments will be created
CALENDAR_ID = 'weddingvowsmanifesto@gmail.com'  # or your actual calendar ID

# ===============================
# AUTHENTICATION SETUP
# ===============================

# Authenticate using service account credentials
# Service accounts allow server applications to access Google APIs without user interaction
# The credentials file contains the private key and other auth information
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# ===============================
# CALENDAR FUNCTIONS
# ===============================

def create_event(summary, start_dt, email=None):  
    """
    Creates a new appointment event in Google Calendar
    """
    
    # Build the Google Calendar API service client using our authenticated credentials
    service = build("calendar", "v3", credentials=creds)

    # Calculate appointment end time
    # CBT (Cognitive Behavioral Therapy) sessions are typically 50 minutes long
    end_dt = start_dt + timedelta(minutes=50)  # CBT session = 50 mins

    # Create the event data structure that Google Calendar expects
    event = {
        'summary': summary,  # Event title that appears in the calendar
        # Start time with timezone (Singapore time zone for local clinic)
        'start': {
            'dateTime': start_dt.isoformat(),  # Convert datetime to ISO format string
            'timeZone': 'Asia/Singapore'       # Set timezone for accurate local time
        },
        # End time with same timezone
        'end': {
            'dateTime': end_dt.isoformat(),    # 50 minutes after start time
            'timeZone': 'Asia/Singapore'
        },
        # Note: Attendees/invites are commented out to avoid Google API permission errors
    }

    # Actually create the event in Google Calendar using the Calendar API
    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    
    # Return the web URL where the event can be viewed/edited
    # This link can be shared with the patient or staff for easy access
    return created_event.get('htmlLink')