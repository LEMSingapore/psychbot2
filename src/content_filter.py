# src/content_filter.py - SIMPLIFIED VERSION
# Remove complex regex, just use simple keyword checks

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
        # Words that suggest mental health crisis - triggers safety response
        self.crisis_words = ['suicide', 'kill myself', 'end my life', 'hurt myself', 'self harm']
        
        # Words related to clinic services - helps identify relevant messages
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
            - False means stop and return the response_message
        """
        message_lower = message.lower()
        
        # Quick clinic check - if clinic-related, allow immediately
        # This handles the most common case first for speed
        if any(word in message_lower for word in self.clinic_words):
            return True, ""
        
        # Crisis check - safety is priority
        # If we find crisis language, stop processing and give crisis resources
        if any(word in message_lower for word in self.crisis_words):
            return False, "If you're having thoughts of self-harm, please call 1800-221-4444 (Singapore) or 995 for emergency."
        
        # Default: allow everything else
        # Most messages will be general questions about therapy/mental health
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
        """Set up the content filter."""
        self.content_filter = ContentFilter()
    
    def process_message(self, message: str) -> Tuple[bool, str]:
        """
        Process incoming message through all safety checks.
        
        Currently just does content filtering, but structured to easily
        add more guardrails later.
        
        Args:
            message: User's input message
            
        Returns:
            Tuple: (continue_processing, safety_response)
        """
        return self.content_filter.check_content(message)