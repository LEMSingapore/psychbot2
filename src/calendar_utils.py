# src/calendar_utils.py
# Google Calendar integration utilities for PsychBot appointment booking.
# Handles creating therapy session appointments directly in Dr. Sarah Tan's Google Calendar (weddingvowsmanifesto@gmail.com)

# Google API client libraries for Calendar integration
from googleapiclient.discovery import build  # Main Google API client builder
from google.oauth2 import service_account  # Service account authentication (server-to-server)
from datetime import timedelta  # For calculating appointment end times

# ===============================
# CONFIGURATION
# ===============================

# Google Calendar API permissions
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Service account file with authentication keys
# Allows app to access calendar without user login
SERVICE_ACCOUNT_FILE = 'credentials.json'

# Target calendar for appointments
CALENDAR_ID = 'weddingvowsmanifesto@gmail.com'

# ===============================
# AUTHENTICATION
# ===============================

# Set up authentication using service account
# This lets the booking system create events automatically
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# ===============================
# CALENDAR FUNCTIONS
# ===============================

def create_event(summary, start_dt, email=None):  
    """
    Create appointment in Google Calendar.
    
    Takes appointment details and adds them to the clinic calendar.
    Standard therapy sessions are 50 minutes long.
    """
    
    # Connect to Google Calendar API
    service = build("calendar", "v3", credentials=creds)

    # Calculate end time - therapy sessions are 50 minutes
    end_dt = start_dt + timedelta(minutes=50)

    # Build event data for Google Calendar
    event = {
        'summary': summary,  # Event title
        'start': {
            'dateTime': start_dt.isoformat(),  # Start time in ISO format
            'timeZone': 'Asia/Singapore'       # Singapore timezone
        },
        'end': {
            'dateTime': end_dt.isoformat(),    # End time (50 mins later)
            'timeZone': 'Asia/Singapore'
        },
        # Note: Attendees disabled to avoid permission issues
    }

    # Create the event in Google Calendar
    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    
    # Return link to view the created event
    return created_event.get('htmlLink')