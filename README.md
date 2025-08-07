# PsychBot

A RAG-powered virtual receptionist for Dr. Sarah Tan's psychotherapy clinic. PsychBot demonstrates advanced AI capabilities including document ingestion, vector search, and intelligent conversation flows for booking appointments.

## Key Features

- 🤖 **RAG (Retrieval-Augmented Generation)** - Intelligent responses using clinic documents
- 📚 **Document Ingestion** - Processes text files into searchable knowledge base
- 🔍 **Vector Search** - Semantic document retrieval using embeddings
- 📅 **Appointment Booking** - Step-by-step guided booking with validation
- 🛡️ **Content Filtering** - Safety guardrails for appropriate conversations
- 🏥 **Medical Website Integration** - Embeds seamlessly into existing websites

---

## Technical Stack

- **Backend**: FastAPI + Python
- **AI Framework**: LangChain + Ollama (Llama 3)
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Integrations**: Google Calendar + SendGrid Email
- **Frontend**: Vanilla HTML/CSS/JavaScript

---

## 🛠️ Quickstart

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/download) with `llama3:latest` model installed
- Optional: Google service account (`credentials.json`)
- Optional: SendGrid API key

---

### Installation

```bash
# Clone the repo
git clone https://github.com/LEMSingapore/psychbot2.git
cd psychbot2

# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required Python packages
pip install -r requirements.txt
```

---

### Setup Ollama (Required)

```bash
# Pull and run the Llama 3 model
ollama pull llama3:latest
ollama serve
```

> Leave Ollama running in a separate terminal tab or window.

---

### Optional: Email/Calendar Configuration

Create a `.env` file in the root project directory:

```env
SENDGRID_API_KEY=your-sendgrid-api-key
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
```

Ensure `credentials.json` is also in the root folder.

---

### Running the Demo

```bash
# 1. Prepare the knowledge base
python src/ingest.py

# 2. Start the backend API
python main.py

# 3. Open the chatbot interface
open simple_mockup.html  # Or double-click the file
```

Ask questions like:

- "What services do you offer?"
- "How much does therapy cost?"
- "I want to book an appointment"

---

## 📁 Project Structure

```
psychbot2/
├── README.md
├── requirements.txt
├── main.py
├── simple_mockup.html
├── credentials.json         # Optional
├── .env                     # Optional
│
├── src/
│   ├── models.py
│   ├── booking_service.py
│   ├── rag_chain.py
│   ├── content_filter.py
│   ├── calendar_utils.py
│   ├── email_utils.py
│   └── ingest.py
│
├── data/
│   ├── clinic_info.txt
│   ├── services.txt
│   └── faq.txt
│
└── docs/                    # ChromaDB vector store (auto-generated)
```

---

## 💡 Demo Highlights

### 1. Document Ingestion
```bash
python src/ingest.py
```

Converts text files into vector embeddings for semantic search.

### 2. Chatbot Embedding
Demo page shows how PsychBot can be embedded into existing websites.

### 3. Smart Conversations
AI retrieves document snippets and generates human-like responses.

### 4. Appointment Booking
Type "book appointment" and go through the full flow:
- Collects patient info
- Validates date/time and NRIC
- Sends confirmation via email (if enabled)

### 5. Guardrails
Handles self-harm or irrelevant questions by:
- Redirecting to professional help
- Steering back to clinic services

---

## ⚙️ Design Features

- **Single-Session Design** – Easy to understand and reset
- **Modular Services** – Each function is independently testable
- **Fallback-Ready** – Works even if calendar/email APIs are missing
- **Beginner-Friendly** – Clear separation between AI logic and backend code

---

## License

This project is licensed under the MIT License.
