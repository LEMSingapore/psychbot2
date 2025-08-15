# PsychBot

A smart chatbot for Dr. Sarah Tan's therapy clinic. It can answer questions and help patients book appointments.

## What It Does

- 🤖 **Smart Answers** - Uses clinic documents to answer questions
- 📚 **Document Reading** - Reads text files to learn about the clinic
- 🔍 **Smart Search** - Finds the right information quickly
- 📅 **Book Appointments** - Helps patients schedule visits
- 🛡️ **Safety Features** - Keeps conversations appropriate
- 🏥 **Website Ready** - Can be added to any website

---

## What You Need

- **Python** (version 3.8 or newer)
- **Ollama** (AI software that runs on your computer)
- **Windows Terminal** or **PowerShell**
- Optional: Email and calendar setup

---

## Step 1: Get Python

### If You Don't Have Python Yet:

**Easy Way (Microsoft Store):**
1. Press Windows key
2. Type "Microsoft Store" and open it
3. Search for "Python 3.11"
4. Click "Install"

### Test If Python Works:
Open PowerShell and type:
```powershell
python --version
```
You should see something like "Python 3.11.x"

---

## Step 2: Download This Project

```powershell
# Download the project
git clone https://github.com/LEMSingapore/psychbot2.git
cd psychbot2
```

Or download the ZIP file from GitHub and unzip it.

---

## Step 3: Set Up Python Environment

```powershell
# Make a clean Python space for this project
python -m venv venv

# Turn it on (Command Prompt)
venv\Scripts\activate

# Turn it on (PowerShell)
venv\Scripts\Activate.ps1
```

```powershell
# Install the needed Python packages
pip install -r requirements.txt
```

---

## Step 4: Get Ollama (The AI Brain)

1. Go to [ollama.com](https://ollama.com/download)
2. Download Ollama for Windows
3. Install it (it will start automatically)
4. Open Command Prompt or PowerShell and type:

```powershell
# Download the AI model
ollama pull llama3:latest

# Check if it's working
curl http://localhost:11434
```

If the last command shows "Ollama is running" - you're good!

---

## Step 5: Optional - Email and Calendar Setup

**You can skip this step if you just want to test the chatbot.**

If you want the chatbot to send emails and check calendars:

### For Email (SendGrid):
1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Get your API key from the dashboard
3. Create a file called `.env` in your project folder
4. Add this line to the `.env` file:
```
SENDGRID_API_KEY=your-api-key-here
```

### For Google Calendar:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the Google Calendar API
4. Create a service account
5. Download the JSON file
6. Rename it to `credentials.json`
7. Put it in your project folder
8. Add this line to your `.env` file:
```
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
```

Your `.env` file should look like:
```
SENDGRID_API_KEY=your-sendgrid-api-key
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
```

---

## Step 6: Run the Chatbot

```powershell
# Make sure your Python environment is on
# You should see (venv) at the start of your line

# Prepare the chatbot's knowledge
python src/ingest.py

# Start the chatbot server
python main.py

# Open the chat page
start simple_mockup.html
```

Now you can chat with the bot! Try asking:
- "What services do you offer?"
- "How much does therapy cost?"
- "I want to book an appointment"

---

## Project Files

```
psychbot2/
├── README.md              # This file
├── requirements.txt       # Python packages needed
├── main.py               # Main server file
├── simple_mockup.html    # Chat webpage
├── .env                  # Optional: Email/calendar settings
├── credentials.json      # Optional: Google calendar file
│
├── src/                  # Python code
├── data/                 # Clinic information files
├── docs/                 # AI knowledge (created automatically)
└── venv/                 # Python environment (you create this)
```

---

## What the Chatbot Can Do

1. **Answer Questions** - About clinic services, prices, hours
2. **Book Appointments** - Collects patient info and schedules visits
3. **Stay Safe** - Redirects serious questions to real doctors
4. **Learn** - Uses clinic documents to give accurate answers

---

## License

This project is free to use (MIT License).