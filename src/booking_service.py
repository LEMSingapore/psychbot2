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

class BookingStep(Enum):
    """Booking flow steps"""
    NOT_STARTED = "not_started"
    COLLECT_NAME = "collect_name"
    COLLECT_NRIC = "collect_nric"
    COLLECT_DATE = "collect_date"
    COLLECT_TIME = "collect_time"
    COLLECT_EMAIL = "collect_email"
    COMPLETED = "completed"

class BookingService:
    """Speed-optimized booking service with pre-compiled patterns"""
    
    def __init__(self):
        """Initialize with pre-compiled regex for speed"""
        self.current_step = BookingStep.NOT_STARTED
        self.booking_data = {}
        
        # PRE-COMPILED PATTERNS for faster validation
        self.nric_pattern = re.compile(r'^[STFG]\d{7}[A-Z]$', re.IGNORECASE)
        self.email_pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        self.time_pattern = re.compile(r'^(\d{1,2})(?::(\d{2}))?\s*(am|pm)$', re.IGNORECASE)
        self.date_pattern = re.compile(
            r'^(?:(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)|'
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2}))$',
            re.IGNORECASE
        )
        
        # FAST LOOKUP for months (no regex needed)
        self.month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        # PRE-DEFINED booking triggers (set lookup is O(1))
        self.booking_triggers = {
            'book', 'appointment', 'schedule', 'booking', 'reserve'
        }
    
    def is_booking_trigger(self, message: str) -> bool:
        """Simple booking trigger detection"""
        message_lower = message.lower()
        return any(word in message_lower for word in ['book', 'appointment', 'schedule', 'booking'])
    
    def get_or_create_guided_session(self, message: str) -> str:
        """Always start fresh session"""
        self._reset_session()
        return "current"
    
    def process_guided_booking_step(self, session_id: str, message: str) -> str:
        """Optimized step processing"""
        message = message.strip()
        
        # STATE MACHINE with early returns for speed
        if self.current_step == BookingStep.NOT_STARTED:
            self.current_step = BookingStep.COLLECT_NAME
            return "Let's book your appointment!\n\nWhat's your full name?"
        
        elif self.current_step == BookingStep.COLLECT_NAME:
            if len(message) >= 2:  # Fast validation
                self.booking_data['name'] = message
                self.current_step = BookingStep.COLLECT_NRIC
                return f"Thanks {message}!\n\nYour NRIC? (e.g., S1234567A)"
            return "Please provide your full name."
        
        elif self.current_step == BookingStep.COLLECT_NRIC:
            nric = message.upper().replace(' ', '')  # Fast cleanup
            if self.nric_pattern.match(nric):  # Pre-compiled regex
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
    
    def _process_date_input(self, date_str: str) -> str:
        """Fast date processing with pre-compiled regex"""
        match = self.date_pattern.match(date_str.strip().lower())
        if not match:
            return "Please use format like '15 Aug' or 'Aug 15'."
        
        try:
            # Fast parsing using match groups
            if match.group(1):  # "15 Aug" format
                day, month_str = int(match.group(1)), match.group(2)
            else:  # "Aug 15" format
                month_str, day = match.group(3), int(match.group(4))
            
            month = self.month_map[month_str]  # O(1) lookup
            appointment_date = date(datetime.now().year, month, day)
            
            # Quick validation
            if appointment_date <= date.today():
                return "Please choose a future date."
            if appointment_date.weekday() == 6:  # Sunday
                return "We're closed Sundays. Choose Monday-Saturday."
            
            # Store and proceed
            self.booking_data['date'] = appointment_date.strftime('%Y-%m-%d')
            self.booking_data['date_formatted'] = appointment_date.strftime('%B %d, %Y')
            self.current_step = BookingStep.COLLECT_TIME
            
            return f"Perfect! {self.booking_data['date_formatted']}.\n\nWhat time? (e.g., '2pm' or '10:30am')"
            
        except (ValueError, KeyError):
            return "Please use a valid date like '15 Aug' or 'Aug 15'."
    
    def _process_time_input(self, time_str: str) -> str:
        """Fast time processing with pre-compiled regex"""
        match = self.time_pattern.match(time_str.strip().lower())
        if not match:
            return "Please use format like '2pm' or '10:30am'."
        
        try:
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)  # Default to 0 if no minutes
            ampm = match.group(3)
            
            # Fast 12-hour to 24-hour conversion
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
            
            # Quick business hours check
            if not (9 <= hour <= 17):
                return "Please choose between 9:00 AM and 5:00 PM."
            
            # Store and proceed
            time_24 = f"{hour:02d}:{minute:02d}"
            time_formatted = datetime.strptime(time_24, '%H:%M').strftime('%I:%M %p')
            
            self.booking_data['time'] = time_24
            self.booking_data['time_formatted'] = time_formatted
            self.current_step = BookingStep.COLLECT_EMAIL
            
            return f"Excellent! {self.booking_data['date_formatted']} at {time_formatted}.\n\nYour email address?"
            
        except ValueError:
            return "Please use valid time like '2pm' or '10:30am'."
    
    def _process_email_input(self, email_str: str) -> str:
        """Fast email processing and booking completion"""
        email = email_str.strip().lower()
        
        if not self.email_pattern.match(email):  # Pre-compiled regex
            return "Please provide a valid email address."
        
        self.booking_data['email'] = email
        
        # COMPLETE BOOKING (keep existing logic but add error handling)
        try:
            appointment_date = datetime.strptime(self.booking_data['date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(self.booking_data['time'], '%H:%M').time()
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            
            # Create calendar event and send email
            create_event(
                summary=f"Therapy - {self.booking_data['name']}",
                start_dt=appointment_datetime,
                email=email
            )
            
            send_confirmation(
                to_email=email,
                name=self.booking_data['name'],
                dt=appointment_datetime
            )
            
            # Success message
            success_msg = f"""✅ Booking confirmed!

{self.booking_data['name']} - {self.booking_data['nric']}
{appointment_datetime.strftime('%A, %B %d at %I:%M %p')}

Confirmation sent to {email}
Location: Level 8, Raffles Specialist Centre

To reschedule: +65 6311 2330"""
            
            self._reset_session()
            return success_msg
            
        except Exception as e:
            logger.error(f"Booking error: {e}")
            self._reset_session()
            return "Booking error occurred. Please call +65 6311 2330."
    
    def _reset_session(self):
        """Fast session reset"""
        self.current_step = BookingStep.NOT_STARTED
        self.booking_data.clear()  # Faster than creating new dict
