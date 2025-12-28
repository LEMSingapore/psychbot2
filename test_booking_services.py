#!/usr/bin/env python3
"""
Test script to diagnose booking service issues.
Tests Google Calendar and SendGrid connections individually.
"""

import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("BOOKING SERVICES DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Google Calendar API
print("\n1. Testing Google Calendar API...")
try:
    from src.calendar_utils import create_event

    # Try creating a test event
    test_time = datetime.now() + timedelta(days=7)
    event_link = create_event(
        summary="TEST - Booking System Test",
        start_dt=test_time,
        email=None
    )
    print("   ✓ Google Calendar API: SUCCESS")
    print(f"   Event link: {event_link}")

except Exception as e:
    print(f"   ✗ Google Calendar API: FAILED")
    print(f"   Error: {type(e).__name__}: {str(e)}")
    print("\n   Possible fixes:")
    print("   - Check credentials.json exists and is valid")
    print("   - Verify service account has calendar access")
    print("   - Share calendar with service account email")

# Test 2: Gmail SMTP Email API
print("\n2. Testing Gmail SMTP Email API...")
try:
    from src.email_utils import send_confirmation
    import os

    # Check if Gmail credentials exist
    gmail_address = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_address:
        raise ValueError("GMAIL_ADDRESS not found in environment")
    if not gmail_password:
        raise ValueError("GMAIL_APP_PASSWORD not found in environment")

    # Try sending a test email
    test_time = datetime.now() + timedelta(days=7)
    send_confirmation(
        to_email=gmail_address,  # Send to self for testing
        name="Test User",
        dt=test_time
    )
    print("   ✓ Gmail SMTP Email API: SUCCESS")
    print(f"   Test email sent to {gmail_address}")

except ValueError as e:
    print(f"   ✗ Gmail SMTP Email API: FAILED")
    print(f"   Error: {str(e)}")
    print("\n   Possible fixes:")
    print("   - Add GMAIL_ADDRESS and GMAIL_APP_PASSWORD to .env file")
    print("   - Get App Password from https://myaccount.google.com/apppasswords")
    print("   - Make sure 2-Step Verification is enabled on your Google account")

except Exception as e:
    print(f"   ✗ Gmail SMTP Email API: FAILED")
    print(f"   Error: {type(e).__name__}: {str(e)}")
    print("\n   Possible fixes:")
    print("   - Verify GMAIL_APP_PASSWORD is correct (16 characters, no spaces)")
    print("   - Make sure 2-Step Verification is enabled on Gmail")
    print("   - Check that 'Less secure app access' is NOT required (App Passwords don't need it)")

print("\n" + "=" * 60)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 60)
