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

## Quickstart

### Prerequisites

* Python 3.8 or higher
* Ollama with Llama 3 model installed
* Google service account credentials (`credentials.json`) - optional
* SendGrid API key - optional

### Installation

```bash
git clone https://github.com/your-username/psychbot.git
cd psychbot
pip install -r requirements.txt
```

### Setup Ollama (Required)

```bash
# Install Ollama (see https://ollama.ai)
ollama pull llama3:latest
ollama serve
```

### Configuration (Optional)

Create a `.env` file for email/calendar integration:

```env
SENDGRID_API_KEY=YOUR_SENDGRID_API_KEY
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
```

### Running the Demo

1. **Prepare the knowledge base**
   ```bash
   python src/ingest.py
   ```

2. **Start the backend API**
   ```bash
   python main.py
   ```

3. **Open the demo page**
   ```bash
   # Open simple_mockup.html in your browser
   open simple_mockup.html
   ```

4. **Try the chatbot** - Click the brain icon and ask questions like:
   - "What services do you offer?"
   - "How much does therapy cost?"
   - "I want to book an appointment"

---

## Project Structure

```
psychbot/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── main.py                   # FastAPI application entry point
├── simple_mockup.html        # Demo webpage with embedded chatbot
├── credentials.json          # Google API credentials (optional)
├── .env                      # Environment variables (optional)
│
├── src/                      # Source code modules
│   ├── models.py             # Pydantic data models
│   ├── booking_service.py    # Single-session appointment booking
│   ├── rag_chain.py          # RAG implementation with LangChain
│   ├── content_filter.py     # Safety and content filtering
│   ├── calendar_utils.py     # Google Calendar integration
│   ├── email_utils.py        # SendGrid email service
│   └── ingest.py             # Document ingestion pipeline
│
├── data/                     # Clinic information documents
│   ├── clinic_info.txt       # Basic clinic information
│   ├── services.txt          # Therapy services and pricing
│   └── faq.txt               # Frequently asked questions
│
└── docs/                     # Generated vector database
    └── (ChromaDB files created by ingest.py)
```

---

## Demo Workflow

### 1. Document Ingestion Demo
```bash
python src/ingest.py
```
Shows how text documents are processed into vector embeddings for semantic search.

### 2. Integration Demo
The HTML mockup shows how PsychBot embeds into a real medical website without disrupting the existing design.

### 3. RAG Conversation Demo
Ask questions about the clinic - the system will:
1. Convert your question to vectors
2. Search for relevant document chunks
3. Generate contextual responses using Llama 3

### 4. Booking Flow Demo
Type "book appointment" to see the guided booking system:
1. Collects patient information step-by-step
2. Validates inputs (NRIC, date/time formats)
3. Creates calendar events and sends confirmations

### 5. Guardrails for Privacy and Ethics
Ask irrevalent questions about the clinic or Dr Tan, or some self-harm comments - the system will:
1. Provide some self-harm prevention information (on the topic of self-harm)
2. Reject the question and steer the patient back to the clinic's services or provide appointment booking assistance (on the topic of irrelevant or privacy matters)

---

## Key Architecture Features

- **Single Session Design** - Simplified state management for demos
- **Synchronous RAG** - Synchronous handling makes it easier to understand
- **Modular Components** - Each service is independently testable
- **Graceful Fallbacks** - Demo responses when external services unavailable

---

## Development

The codebase is designed for for educational demos only:

- Simplified synchronous handling for easier understanding
- Mock integrations that can be easily replaced with real services (simple_mockup.html)
- Comprehensive comments explaining RAG concepts and Business functionalities
- Clean separation between AI logic and business logic

---

## License

This project is licensed under the MIT License.