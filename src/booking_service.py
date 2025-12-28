# src/booking_service.py - SPEED OPTIMIZED
# Fast booking service with pre-compiled patterns and minimal processing

import re
from datetime import datetime, date, time as dt_time
from enum import Enum
from typing import Tuple
from functools import lru_cache
import logging

# Import utilities (keep these as-is)
from .calendar_utils import create_event
from .email_utils import send_confirmation

logger = logging.getLogger(__name__)

# ===============================
# BOOKING STATE MANAGEMENT
# ===============================

class BookingStep(Enum):
    """
    Tracks which step of booking we're on - like a checklist.
    
    Booking flow: Name → NRIC → Date → Time → Email → Done
    Each step asks for different information from the user.
    """
    NOT_STARTED = "not_started"    # No booking in progress
    COLLECT_NAME = "collect_name"  # Asking for patient's full name
    COLLECT_NRIC = "collect_nric"  # Asking for Singapore ID number
    COLLECT_DATE = "collect_date"  # Asking for appointment date
    COLLECT_TIME = "collect_time"  # Asking for appointment time
    COLLECT_EMAIL = "collect_email" # Asking for email address
    COMPLETED = "completed"        # Booking is finished

# ===============================
# MAIN BOOKING SERVICE CLASS
# ===============================

class BookingService:
    """
    Handles the complete appointment booking process.
    
    Works like a conversation - asks questions one by one,
    validates each answer, then moves to the next question.
    """
    
    def __init__(self):
        """
        Set up the booking system with fast validation patterns.
        
        Pre-compiles all regex patterns for speed - compiling patterns
        is slow, so we do it once here instead of every time we validate.
        """
        # Track where we are in booking process
        self.current_step = BookingStep.NOT_STARTED
        self.booking_data = {}  # Store user info as we collect it
        
        # PRE-MADE PATTERNS - compile once, use many times for speed
        
        # Singapore NRIC: Letter + 7 numbers + Letter (like S1234567A)
        self.nric_pattern = re.compile(r'^[STFG]\d{7}[A-Z]$', re.IGNORECASE)
        
        # Basic email check: something@something.something
        self.email_pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        
        # Time formats: "2pm", "10:30am" etc.
        self.time_pattern = re.compile(r'^(\d{1,2})(?::(\d{2}))?\s*(am|pm)$', re.IGNORECASE)
        
        # Date formats: "15 Aug" or "Aug 15"
        self.date_pattern = re.compile(
            r'^(?:(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)|'
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2}))$',
            re.IGNORECASE
        )
        
        # Fast month lookup - dictionary is faster than regex
        self.month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        # Words that start booking - set lookup is faster than list
        self.booking_triggers = {
            'book', 'appointment', 'schedule', 'booking', 'reserve'
        }
    
    # ===============================
    # BOOKING DETECTION
    # ===============================
    
    def is_booking_trigger(self, message: str) -> bool:
        """
        Check if user wants to start booking an appointment.
        
        Looks for booking-related keywords in their message.
        Returns True if we should start the booking conversation.
        """
        message_lower = message.lower()
        # Stop checking as soon as we find a booking word
        return any(word in message_lower for word in ['book', 'appointment', 'schedule', 'booking'])
    
    def get_or_create_guided_session(self, message: str) -> str:
        """
        Start a fresh booking session.
        
        Always clears old data to prevent mixing up different bookings.
        Returns a session ID (we just use "current" since one user at a time).
        """
        self._reset_session()
        return "current"
    
    # ===============================
    # MAIN BOOKING CONVERSATION HANDLER
    # ===============================
    
    def process_guided_booking_step(self, session_id: str, message: str) -> str:
        """
        Handle each step of booking. Works like a state machine - each step
        checks input, saves good data, moves to next step.
        
        Returns early to avoid extra work.
        """
        message = message.strip()
        
        # Handle each booking step
        if self.current_step == BookingStep.NOT_STARTED:
            # Start booking process
            self.current_step = BookingStep.COLLECT_NAME
            return "Let's book your appointment!\n\nWhat's your full name?"
        
        elif self.current_step == BookingStep.COLLECT_NAME:
            # Check name is long enough
            if len(message) >= 2:
                self.booking_data['name'] = message
                self.current_step = BookingStep.COLLECT_NRIC
                return f"Thanks {message}!\n\nYour NRIC? (e.g., S1234567A)"
            return "Please provide your full name."
        
        elif self.current_step == BookingStep.COLLECT_NRIC:
            # Clean and check NRIC format
            nric = message.upper().replace(' ', '')
            if self.nric_pattern.match(nric):
                self.booking_data['nric'] = nric
                self.current_step = BookingStep.COLLECT_DATE
                return "Great!\n\nPreferred date? (e.g., '15 Aug' or 'Aug 15')"
            return "Please provide valid NRIC (e.g., S1234567A)."
        
        elif self.current_step == BookingStep.COLLECT_DATE:
            return self._process_date_input(message)
        
        elif self.current_step == BookingStep.COLLECT_TIME:
            return self._process_time_input(message)
        
        elif self.current_step == BookingStep.COLLECT_EMAIL:
            return self._process_email_input(message)
        
        return "Something went wrong. Type 'book appointment' to restart."
    
    # ===============================
    # INPUT PROCESSING METHODS
    # ===============================
    
    def _process_date_input(self, date_str: str) -> str:
        """
        Check date input and make sure it's valid.
        
        Handles "15 Aug" and "Aug 15" formats.
        Checks business rules: must be future date, not Sunday.
        """
        # Check if date format is right
        match = self.date_pattern.match(date_str.strip().lower())
        if not match:
            return "Please use format like '15 Aug' or 'Aug 15'."
        
        try:
            # Get day and month from the pattern match
            if match.group(1):  # "15 Aug" format
                day, month_str = int(match.group(1)), match.group(2)
            else:  # "Aug 15" format
                month_str, day = match.group(3), int(match.group(4))
            
            # Convert month name to number
            month = self.month_map[month_str]
            appointment_date = date(datetime.now().year, month, day)
            
            # Check business rules
            if appointment_date <= date.today():
                return "Please choose a future date."
            if appointment_date.weekday() == 6:  # Sunday
                return "We're closed Sundays. Choose Monday-Saturday."
            
            # Save date in two formats: one for system, one for user
            self.booking_data['date'] = appointment_date.strftime('%Y-%m-%d')
            self.booking_data['date_formatted'] = appointment_date.strftime('%B %d, %Y')
            self.current_step = BookingStep.COLLECT_TIME
            
            return f"Perfect! {self.booking_data['date_formatted']}.\n\nWhat time? (e.g., '2pm' or '10:30am')"
            
        except (ValueError, KeyError):
            return "Please use a valid date like '15 Aug' or 'Aug 15'."
    
    def _process_time_input(self, time_str: str) -> str:
        """
        Check time input and convert to 24-hour format.
        
        Handles "2pm", "10:30am" etc.
        Checks clinic hours: 9 AM to 5 PM only.
        """
        match = self.time_pattern.match(time_str.strip().lower())
        if not match:
            return "Please use format like '2pm' or '10:30am'."
        
        try:
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)  # Default to 0 if no minutes
            ampm = match.group(3)
            
            # Convert 12-hour to 24-hour time
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
            
            # Check clinic hours
            if not (9 <= hour <= 17):
                return "Please choose between 9:00 AM and 5:00 PM."
            
            # Save time in both formats
            time_24 = f"{hour:02d}:{minute:02d}"
            time_formatted = datetime.strptime(time_24, '%H:%M').strftime('%I:%M %p')
            
            self.booking_data['time'] = time_24
            self.booking_data['time_formatted'] = time_formatted
            self.current_step = BookingStep.COLLECT_EMAIL
            
            return f"Excellent! {self.booking_data['date_formatted']} at {time_formatted}.\n\nYour email address?"
            
        except ValueError:
            return "Please use valid time like '2pm' or '10:30am'."
    
    def _process_email_input(self, email_str: str) -> str:
        """
        Check email and complete the booking.
        
        This is the final step - validates email, then:
        1. Creates calendar event
        2. Sends confirmation email
        3. Shows success message
        4. Cleans up for next booking
        """
        email = email_str.strip().lower()
        
        # Check email format
        if not self.email_pattern.match(email):
            return "Please provide a valid email address."
        
        self.booking_data['email'] = email
        
        # Complete the booking
        try:
            # Convert saved date/time back to datetime object
            appointment_date = datetime.strptime(self.booking_data['date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(self.booking_data['time'], '%H:%M').time()
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            
            # Create calendar event
            create_event(
                summary=f"Therapy - {self.booking_data['name']}",
                start_dt=appointment_datetime,
                email=email
            )

            # Try to send email confirmation (optional - don't fail if it doesn't work)
            email_sent = False
            try:
                send_confirmation(
                    to_email=email,
                    name=self.booking_data['name'],
                    dt=appointment_datetime
                )
                email_sent = True
            except Exception as email_error:
                logger.warning(f"Email sending failed (non-critical): {email_error}")

            # Show success message with all details
            email_status = f"Confirmation sent to {email}" if email_sent else f"Email: {email} (confirmation pending)"
            success_msg = f"""✅ Booking confirmed!

{self.booking_data['name']} - {self.booking_data['nric']}
{appointment_datetime.strftime('%A, %B %d at %I:%M %p')}

{email_status}
Location: Level 8, Raffles Specialist Centre

To reschedule: +65 6311 2330"""
            
            self._reset_session()
            return success_msg
            
        except Exception as e:
            # If anything goes wrong, log it and give phone number
            logger.error(f"Booking error: {e}", exc_info=True)
            self._reset_session()
            return f"Booking error occurred: {str(e)}\n\nPlease call +65 6311 2330 to book manually."
    
    # ===============================
    # SESSION CLEANUP
    # ===============================
    
    def _reset_session(self):
        """
        Clear booking data for fresh start.
        Called after booking complete or when errors happen.
        """
        self.current_step = BookingStep.NOT_STARTED
        self.booking_data.clear()  # Faster than making new dict