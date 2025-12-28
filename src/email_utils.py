# src/email_utils.py
# Email notification utilities for PsychBot appointment confirmations
# Handles sending appointment confirmation emails to patients using Gmail SMTP.

import os  # For accessing environment variables
import smtplib  # Built-in Python SMTP client
from email.mime.text import MIMEText  # For creating email messages
from email.mime.multipart import MIMEMultipart  # For HTML emails
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load API keys and secrets from .env file
load_dotenv()

# ===============================
# EMAIL CONFIGURATION
# ===============================

# Gmail SMTP settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLS port
SMTP_USERNAME = os.getenv("GMAIL_ADDRESS", "weddingvowsmanifesto@gmail.com")
SMTP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # App password, not regular password

# ===============================
# EMAIL FUNCTIONS
# ===============================

def send_confirmation(to_email, name, dt):
    """
    Send appointment confirmation email to patient using Gmail SMTP.

    Creates HTML email with appointment details and clinic info.
    Requires Gmail App Password in environment variables.
    """

    # Format datetime for user display
    # Example: "Monday, 15 January 2024 at 2:30 PM"
    formatted_dt = dt.strftime("%A, %d %B %Y at %I:%M %p")

    # Create email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Appointment with Dr. Tan is Confirmed"
    message["From"] = SMTP_USERNAME
    message["To"] = to_email

    # HTML email content with appointment details and clinic address
    html_content = f"""
    <html>
      <body>
        <p>Hi {name},</p>
        <p>Your appointment is confirmed for <strong>{formatted_dt}</strong>.</p>
        <p>We look forward to seeing you at Level 8, Raffles Specialist Centre, 585 North Bridge Road, Singapore 188770</p>
        <br>
        <p>— Dr. Tan's Clinic</p>
      </body>
    </html>
    """

    # Plain text alternative (for email clients that don't support HTML)
    text_content = f"""
Hi {name},

Your appointment is confirmed for {formatted_dt}.

We look forward to seeing you at Level 8, Raffles Specialist Centre, 585 North Bridge Road, Singapore 188770

— Dr. Tan's Clinic
    """

    # Attach both plain text and HTML versions
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    message.attach(part1)
    message.attach(part2)

    # Send email via Gmail SMTP
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Upgrade connection to secure TLS
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)
