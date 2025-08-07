# src/email_utils.py
# Email notification utilities for PsychBot appointment confirmations
# Handles sending appointment confirmation emails to patients using SendGrid

import os  # For accessing environment variables
from sendgrid import SendGridAPIClient  # Main SendGrid client for API communication
from sendgrid.helpers.mail import Mail  # Email message builder helper
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load environment variables from .env file
# This includes sensitive data like API keys that is not hardcoded here
load_dotenv()

def send_confirmation(to_email, name, dt):
    """
    Sends an appointment confirmation email to the patient

    Process:
    1. Format the datetime into a human-readable string
    2. Create an HTML email with appointment details and clinic address
    3. Send via SendGrid email service
    """
    
    # Format the datetime into a user-friendly format
    # Example: "Monday, 15 January 2024 at 2:30 PM"
    formatted_dt = dt.strftime("%A, %d %B %Y at %I:%M %p")

    # Create the email message using SendGrid's Mail helper
    message = Mail(
        # Sender email (should be verified domain with SendGrid)
        from_email="weddingvowsmanifesto@gmail.com", # Dr Sarah Tan's clinic email address
        
        # Recipient email address (patient's email)
        to_emails=to_email,
        
        # Email subject line - clear and professional
        subject="Your Appointment with Dr. Tan is Confirmed",
        
        # HTML email body with appointment details
        html_content=f"""
        <p>Hi {name},</p>
        <p>Your appointment is confirmed for <strong>{formatted_dt}</strong>.</p>
        <p>We look forward to seeing you at Level 8, Raffles Specialist Centre 585 North Bridge Road Singapore 188770</p>
        <br>
        <p>– Dr. Tan's Clinic</p>
        """
    )
    
    # Initialize SendGrid client with API key from environment variables
    # The API key is stored securely in .env file and loaded via load_dotenv()
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    
    # Send the email via SendGrid's API
    # This handles delivery, bounces, and other email logistics
    sg.send(message)