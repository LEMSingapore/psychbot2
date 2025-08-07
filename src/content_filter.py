# src/content_filter.py - SIMPLIFIED VERSION
# Remove complex regex, just use simple keyword checks

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class ContentFilter:
    """Super simple content filtering - just basic keyword checks"""
    
    def __init__(self):
        # Simple word lists (much faster than regex)
        self.crisis_words = ['suicide', 'kill myself', 'end my life', 'hurt myself', 'self harm']
        self.clinic_words = ['therapy', 'appointment', 'booking', 'schedule', 'services', 'hours', 'cost', 'price']

    def check_content(self, message: str) -> Tuple[bool, str]:
        """Simple keyword-based filtering"""
        message_lower = message.lower()
        
        # Quick clinic check - if clinic-related, allow immediately
        if any(word in message_lower for word in self.clinic_words):
            return True, ""
        
        # Crisis check
        if any(word in message_lower for word in self.crisis_words):
            return False, "If you're having thoughts of self-harm, please call 1800-221-4444 (Singapore) or 995 for emergency."
        
        # Default: allow everything else
        return True, ""

class GuardrailsManager:
    """Simplified guardrails"""
    
    def __init__(self):
        self.content_filter = ContentFilter()
    
    def process_message(self, message: str) -> Tuple[bool, str]:
        """Simple processing"""
        return self.content_filter.check_content(message)
