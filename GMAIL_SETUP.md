# Gmail SMTP Setup Guide

This guide explains how to set up Gmail SMTP for sending appointment confirmation emails.

## Why Gmail SMTP?

- ✅ **Completely free** - No trial periods or payment required
- ✅ **500 emails/day** - More than enough for appointment bookings
- ✅ **Better deliverability** - Emails are less likely to go to spam
- ✅ **Easy setup** - Just need an App Password

## Prerequisites

Your Gmail account must have **2-Step Verification** enabled to use App Passwords.

## Step 1: Enable 2-Step Verification (if not already enabled)

1. Go to https://myaccount.google.com/security
2. Under "Signing in to Google," click **2-Step Verification**
3. Follow the prompts to set it up (usually takes 2-3 minutes)

## Step 2: Generate a Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. You may need to sign in again
3. In the "App name" field, type: **PsychBot**
4. Click **Create**
5. Google will show you a 16-character password (like `abcd efgh ijkl mnop`)
6. **Copy this password** - you won't see it again!

## Step 3: Add to Your Environment Variables

### For Local Development

Edit your `.env` file:

```bash
# Gmail SMTP Configuration
GMAIL_ADDRESS=weddingvowsmanifesto@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop  # Your 16-char password (remove spaces!)
```

**Important:** Remove all spaces from the app password!

### For Render Deployment

1. Go to https://dashboard.render.com
2. Select your PsychBot service
3. Go to **Environment** tab
4. Add two new environment variables:
   - `GMAIL_ADDRESS` = `weddingvowsmanifesto@gmail.com`
   - `GMAIL_APP_PASSWORD` = Your 16-character password (no spaces)
5. Click **Save Changes** (this will trigger a redeploy)

## Step 4: Test the Configuration

Run the test script:

```bash
python test_booking_services.py
```

You should see:
```
2. Testing Gmail SMTP Email API...
   ✓ Gmail SMTP Email API: SUCCESS
   Test email sent to weddingvowsmanifesto@gmail.com
```

Check your inbox at `weddingvowsmanifesto@gmail.com` for the test email!

## Troubleshooting

### "GMAIL_APP_PASSWORD not found in environment"
- Make sure you added it to `.env` file
- Make sure `.env` is in the project root directory
- Restart your application after adding it

### "Authentication failed" or "Username and Password not accepted"
- Double-check the App Password is correct
- Make sure there are NO SPACES in the password
- Verify 2-Step Verification is enabled
- Try generating a new App Password

### "SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')"
- The Gmail address or App Password is incorrect
- Make sure you're using an App Password, not your regular Gmail password
- Try logging into Gmail in a browser to make sure the account isn't locked

## Security Notes

- ✅ App Passwords are safer than your regular password
- ✅ You can revoke App Passwords anytime at https://myaccount.google.com/apppasswords
- ✅ Never commit `.env` file to git (it's already in `.gitignore`)
- ✅ Each app should have its own unique App Password

## Daily Limits

- **Personal Gmail:** 100 emails/day
- **Google Workspace:** 500 emails/day

For a clinic booking system, this is more than sufficient!
