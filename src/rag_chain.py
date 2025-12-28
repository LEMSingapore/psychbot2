# src/rag_chain.py - OPTIMIZED for speed
# Fast RAG system with OpenAI and caching

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from langchain_openai import ChatOpenAI
import os
import logging
from functools import lru_cache
import time

# Set up logging to track performance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===============================
# PERFORMANCE OPTIMIZATIONS
# ===============================

# Load the text embedding model only once and reuse it
@lru_cache(maxsize=1)
def get_embeddings_model():
    """Cached embeddings model - uses OpenAI for low memory footprint"""
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    return OpenAIEmbeddings(
        model="text-embedding-3-small",  # Cheap and efficient: $0.02 per 1M tokens
        openai_api_key=openai_api_key
    )

# Load the language model only once and keep it in memory
@lru_cache(maxsize=1)
def get_llm():
    """Cached LLM - uses OpenAI API for cost-effective cloud deployment"""
    # Get API key from environment (required)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    return ChatOpenAI(
        model="gpt-3.5-turbo",     # Fast and cost-effective model
        temperature=0.1,            # Low randomness = consistent responses
        max_tokens=100,             # Limit response length for cost control
        openai_api_key=openai_api_key,
        request_timeout=10          # 10 second timeout for faster failures
    )

# Load the vector database only once
@lru_cache(maxsize=1)
def get_vector_store():
    """Cached vector store"""
    persist_directory = "docs" # Folder where vectorized documents are stored

    # Make sure the vector database exists
    if not os.path.exists(persist_directory):
        raise FileNotFoundError(f"Vector store directory '{persist_directory}' not found.")
    
    embeddings = get_embeddings_model()
    # Load existing vector database from disk
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def initialize_rag_system():
    """Set up the complete question-answering system"""
    try:
        # Get our cached components
        llm = get_llm()
        db = get_vector_store()
        
        # Set up document retrieval - only get 2 most relevant docs for speed
        retriever = db.as_retriever(search_kwargs={"k": 2})

        # Create a short, focused prompt template for the receptionist bot
        prompt_template = """You are PsychBot, receptionist for Dr. Sarah Tan's clinic.

Be brief (under 40 words). Be helpful.

Services: Individual $120, Couples $180, Family $200, Group $60, Online $100
Hours: Mon-Fri 9AM-7PM, Sat 9AM-5PM
Call: +65 6311 2330

{context}

Q: {question}
A:"""
        # Convert template to LangChain prompt object
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        # Create the complete question-answering chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,                            # Our language model
            chain_type="stuff",                 # Simple chain type - puts all docs in one prompt
            retriever=retriever,                # Document retrieval system
            return_source_documents=False,      # Don't return source docs for speed
            chain_type_kwargs={"prompt": PROMPT} # Use our custom prompt
        )
        
        logger.info("Optimized QA chain created")
        return qa_chain
        
    except Exception as e:
        logger.error(f"Failed to create QA chain: {e}")
        raise

# ===============================
# CACHED RESPONSES FOR COMMON QUESTIONS
# ===============================

# Pre-written answers for frequently asked questions (instant response)
QUICK_RESPONSES = {
    "services": "Individual $120, Couples $180, Family $200, Group $60, Online $100. Book now?",
    "hours": "Mon-Fri 9AM-7PM, Sat 9AM-5PM, closed Sunday. Call +65 6311 2330.",
    "price": "Individual $120, Couples $180, Family $200, Group $60, Online $100. Book?",
    "cost": "Individual $120, Couples $180, Family $200, Group $60, Online $100. Book?",
    "location": "Level 8, Raffles Specialist Centre, 585 North Bridge Road, Singapore 188770.",
    "book": "I can help you book! What's your full name?",
    "appointment": "I can help you book! What's your full name?",
    "hello": "Hi! I'm PsychBot. How can I help with Dr. Sarah Tan's clinic?",
    "hi": "Hi! How can I help with appointments or clinic info?",
    "help": "I help with bookings, prices, hours, services. What do you need?",
    "phone": "Call us at +65 6311 2330 for appointments.",
    "contact": "Call +65 6311 2330 or book online. How can I help?"
}

def get_quick_response(message: str) -> str:
    """Check for common questions and return cached responses"""
    message_lower = message.lower().strip()
    
    for keyword, response in QUICK_RESPONSES.items():
        if keyword in message_lower:
            return response
    return None

# ===============================
# INITIALIZE THE SYSTEM ON STARTUP
# ===============================

try:
    # Create the QA system when this file is imported
    qa_chain = initialize_rag_system()

    # Run a test query to load everything into memory (warm up)
    qa_chain({"query": "test"})
    logger.info("System warmed up and ready")
except Exception as e:
    logger.error(f"Failed to initialize: {e}")
    qa_chain = None

# ===============================
# MAIN FUNCTION TO ANSWER QUESTIONS
# ===============================

def ask_question(question: str) -> str:
    """Process user questions with 3-layer speed optimization"""
    start_time = time.time() # Track how long this takes
    
    try:
        # LAYER 1: Quick responses for common questions (0.001s)
        quick_response = get_quick_response(question)
        if quick_response:
            logger.info(f"Quick response in {time.time() - start_time:.3f}s")
            return quick_response
        
        # LAYER 2: Make sure the AI system is ready
        if qa_chain is None:
            return "System starting up... Please try again in a moment or call +65 6311 2330."
        
        # LAYER 3: Use the full AI system for complex questions
        logger.info(f"Processing: {question[:30]}...") # Log first 30 chars
        result = qa_chain({"query": question})
        response = result["result"]
        
        # Clean up the AI response
        response = response.strip()
        if len(response) > 150:  # Truncate very long responses
            response = response[:150] + "... Call +65 6311 2330."
        
        elapsed = time.time() - start_time
        logger.info(f"RAG response in {elapsed:.3f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return "I'm having technical issues. Please call +65 6311 2330 directly."

# ===============================
# SYSTEM WARM-UP FUNCTION
# ===============================

def preload_system():
    """Run test queries on startup to make the first real query faster"""
    if qa_chain:
        # Test common question types to load everything into memory
        test_queries = ["hello", "services", "hours", "booking"]
        for query in test_queries:
            try:
                qa_chain({"query": query}) # Run each test query
            except:
                pass # Ignore any errors during warm-up
        logger.info("OpenAI system preloaded and warmed up")
