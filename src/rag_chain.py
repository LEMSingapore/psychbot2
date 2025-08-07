# src/rag_chain.py - OPTIMIZED for speed
# Fast RAG system with caching and smaller models

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
import os
import logging
from functools import lru_cache
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===============================
# PERFORMANCE OPTIMIZATIONS
# ===============================

# Cache embeddings to avoid recomputing
@lru_cache(maxsize=1)
def get_embeddings_model():
    """Cached embeddings model - loads once and reuses"""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},  # Explicitly use CPU
        encode_kwargs={'normalize_embeddings': True}  # Faster processing
    )

# Cache LLM to avoid reloading
@lru_cache(maxsize=1) 
def get_llm():
    """Cached LLM - keeps model loaded in memory"""
    return Ollama(
        model="llama3:8b",    # FASTER: 8B model instead of 70B latest
        # SPEED OPTIMIZATIONS for Ollama:
        temperature=0.1,      # Lower creativity = faster generation
        num_predict=80,       # Shorter responses for receptionist
        num_ctx=1024,         # Smaller context window = much faster
        repeat_penalty=1.1,
        top_k=10,            # Reduce vocabulary consideration
        top_p=0.9,
        # Additional speed optimizations:
        num_thread=4,        # Limit CPU threads for consistency
        repeat_last_n=64    # Prevent repetition efficiently
    )

# Cache vector store
@lru_cache(maxsize=1)
def get_vector_store():
    """Cached vector store"""
    persist_directory = "docs"
    if not os.path.exists(persist_directory):
        raise FileNotFoundError(f"Vector store directory '{persist_directory}' not found.")
    
    embeddings = get_embeddings_model()
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def initialize_rag_system():
    """Fast initialization using cached components"""
    try:
        llm = get_llm()
        db = get_vector_store()
        
        # FASTER RETRIEVAL: Only get 2 docs instead of 3
        retriever = db.as_retriever(search_kwargs={"k": 2})

        # ULTRA-SHORT PROMPT for llama3:8b speed optimization
        prompt_template = """You are PsychBot, receptionist for Dr. Sarah Tan's clinic.

Be brief (under 40 words). Be helpful.

Services: Individual $120, Couples $180, Family $200, Group $60, Online $100
Hours: Mon-Fri 9AM-7PM, Sat 9AM-5PM
Call: +65 6311 2330

{context}

Q: {question}
A:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        logger.info("Optimized QA chain created")
        return qa_chain
        
    except Exception as e:
        logger.error(f"Failed to create QA chain: {e}")
        raise

# ===============================
# CACHED RESPONSES FOR COMMON QUESTIONS
# ===============================

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
# GLOBAL QA CHAIN 
# ===============================

try:
    qa_chain = initialize_rag_system()
    # WARM UP: Run a test query to load everything into memory
    qa_chain({"query": "test"})
    logger.info("System warmed up and ready")
except Exception as e:
    logger.error(f"Failed to initialize: {e}")
    qa_chain = None

# ===============================
# FAST QUESTION PROCESSING
# ===============================

def ask_question(question: str) -> str:
    """Optimized question processing with multiple speed layers"""
    start_time = time.time()
    
    try:
        # LAYER 1: Quick responses for common questions (0.001s)
        quick_response = get_quick_response(question)
        if quick_response:
            logger.info(f"Quick response in {time.time() - start_time:.3f}s")
            return quick_response
        
        # LAYER 2: Check if system is ready
        if qa_chain is None:
            return "System starting up... Please try again in a moment or call +65 6311 2330."
        
        # LAYER 3: RAG processing (optimized)
        logger.info(f"Processing: {question[:30]}...")
        result = qa_chain({"query": question})
        response = result["result"]
        
        # Quick post-processing for llama3:8b
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
# PRELOAD OPTIMIZATION
# ===============================

def preload_system():
    """Call this on startup to warm up all components for llama3:8b"""
    if qa_chain:
        # Run test queries to warm up llama3:8b
        test_queries = ["hello", "services", "hours", "booking"]
        for query in test_queries:
            try:
                qa_chain({"query": query})
            except:
                pass
        logger.info("Llama3:8b system preloaded and warmed up")
