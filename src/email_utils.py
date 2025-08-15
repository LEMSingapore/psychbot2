# src/email_utils.py
# Email notification utilities for PsychBot appointment confirmations
# Handles sending appointment confirmation emails to patients using SendGrid

import os  # For accessing environment variables
from sendgrid import SendGridAPIClient  # Main SendGrid client for API communication
from sendgrid.helpers.mail import Mail  # Email message builder helper
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load API keys and secrets from .env file
load_dotenv()

# ===============================
# EMAIL FUNCTIONS
# ===============================

def send_confirmation(to_email, name, dt):
    """
    Send appointment confirmation email to patient.
    
    Creates HTML email with appointment details and clinic info.
    """
    
    # Format datetime for user display
    # Example: "Monday, 15 January 2024 at 2:30 PM"
    formatted_dt = dt.strftime("%A, %d %B %Y at %I:%M %p")

    # Build email message
    message = Mail(
        from_email="weddingvowsmanifesto@gmail.com",  # Clinic email
        to_emails=to_email,                           # Patient email
        subject="Your Appointment with Dr. Tan is Confirmed",
        
        # HTML email with appointment details and clinic address
        html_content=f"""
        <p>Hi {name},</p>
        <p>Your appointment is confirmed for <strong>{formatted_dt}</strong>.</p>
        <p>We look forward to seeing you at Level 8, Raffles Specialist Centre 585 North Bridge Road Singapore 188770</p>
        <br>
        <p>— Dr. Tan's Clinic</p>
        """
    )
    
    # Send email using SendGrid API
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))  # Get API key from environment
    sg.send(message)  # Send the email