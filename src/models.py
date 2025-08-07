# src/models.py - Minimal models (only what's used)
# Pydantic is a data validation library that validates incoming data
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """
    Data model for incoming chat messages from users
    
    This model validates that the request contains a valid message string
    """
    message: str = Field(
        ...,  # Required field (the ellipsis means this field is mandatory)
        example="What services do you provide?",  # Example shown in API docs
        description="User's chat message"  # Description for API documentation
    )

class ChatResponse(BaseModel):
    """
    Data model for outgoing responses from the chatbot
    
    This model ensures all API responses contain a response string
    """
    response: str  # The chatbot's reply message to send back to the user