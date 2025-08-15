# src/content_filter.py - SIMPLIFIED VERSION
# Use simple keyword checks

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# ===============================
# CONTENT FILTER CLASS
# ===============================

class ContentFilter:
    """
    Simple content filter that checks messages for safety issues.
    
    Uses basic keyword matching instead of complex patterns for speed.
    Two main checks:
    1. Crisis detection - finds self-harm language
    2. Clinic topic detection - identifies appointment-related messages
    """
    
    def __init__(self):
        """
        Set up keyword lists for fast checking.
        
        Using simple lists instead of regex patterns because:
        - Much faster for basic keyword matching
        - Easier to maintain and update
        - Less prone to errors than complex patterns
        """
        # Critical words that indicate someone might harm themselves
        # If found, we immediately provide crisis helpline numbers
        self.crisis_words = ['suicide', 'kill myself', 'end my life', 'hurt myself', 'self harm']
        
        # Words that show the user is asking about clinic services
        # Helps us identify legitimate appointment/therapy questions
        self.clinic_words = ['therapy', 'appointment', 'booking', 'schedule', 'services', 'hours', 'cost', 'price']

    def check_content(self, message: str) -> Tuple[bool, str]:
        """
        Check message content for safety issues and relevance.
        
        Flow:
        1. Convert to lowercase for case-insensitive matching
        2. Check if clinic-related first (most common case)
        3. Check for crisis language (safety priority)
        4. Allow everything else by default
        
        Returns:
            Tuple: (should_continue, response_message)
            - True means message is safe to process
            - False means stop here and return the crisis response
        """
        # Make everything lowercase so "SUICIDE" matches "suicide"
        message_lower = message.lower()
        
        # STEP 1: Check for normal clinic questions first
        # This handles 90% of messages - people asking about appointments
        # Return True = continue processing with the RAG system
        if any(word in message_lower for word in self.clinic_words):
            return True, "" # Empty string = no special response needed
        
        # STEP 2: Check for dangerous self-harm language
        # This is the most important check for user safety
        # Return False = stop processing, send crisis response immediately      
        if any(word in message_lower for word in self.crisis_words):
            crisis_response = "If you're having thoughts of self-harm, please call 1800-221-4444 (Singapore) or 995 for emergency."
            return False, crisis_response
        
        # STEP 3: Default behavior for everything else
        # General mental health questions, greetings, etc. are all okay
        # Return True = let the RAG system handle it normally
        return True, ""

# ===============================
# GUARDRAILS MANAGER
# ===============================

class GuardrailsManager:
    """
    Main entry point for content filtering.
    
    Wraps the ContentFilter to provide a clean interface for the main app.
    Could be extended later to include other safety checks like:
    - Spam detection
    - Inappropriate language filtering
    - Rate limiting
    """
    
    def __init__(self):
        """Create the content filter when the manager starts up."""
        self.content_filter = ContentFilter()

    def process_message(self, message: str) -> Tuple[bool, str]:
        """
        Run a user message through all safety checks.
        
        This is the main function that the chatbot calls before
        processing any user message.
        
        Args:
            message: What the user typed to the chatbot
            
        Returns:
            Tuple of (safe_to_continue, emergency_response):
            - If safe_to_continue is True: process message normally
            - If safe_to_continue is False: return emergency_response immediately
        """
        # Currently only does content filtering, but structured so we can
        # easily add more checks here later (spam, inappropriate content, etc.)
        return self.content_filter.check_content(message)