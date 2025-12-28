# main.py - Essential endpoints only with simple optimizations
# Main FastAPI application file for PsychBot - a chatbot receptionist for Dr. Sarah Tan's psychotherapy clinic

# Import FastAPI framework and middleware components
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules for the application's core functionality
from src.models import ChatRequest, ChatResponse
from src.booking_service import BookingService, BookingStep
from src.rag_chain import ask_question
from src.content_filter import GuardrailsManager

# Configure application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastAPI application
app = FastAPI(
    title="PsychBot API",
    description="Chatbot receptionist for Dr. Sarah Tan's psychotherapy clinic",
    version="2.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core service instances
guardrails = GuardrailsManager()
booking_service = BookingService()

# ===============================
# MAIN CHAT ENDPOINT
# ===============================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - handles all user interactions
    """
    start_time = datetime.now()
    
    try:
        message = request.message.strip()
        
        # Simple logging (only for longer messages)
        if len(message) > 5:
            logger.info(f"Received: {message[:30]}...")
        
        # Step 1: Content filtering
        should_continue, guardrail_response = guardrails.process_message(message)
        if not should_continue:
            return ChatResponse(response=guardrail_response)
        
        # Step 2: Booking trigger check
        if booking_service.is_booking_trigger(message):
            session_id = booking_service.get_or_create_guided_session(message)
            response = booking_service.process_guided_booking_step(session_id, message)
            return ChatResponse(response=response)
        
        # Step 3: Continue existing bookings
        if booking_service.current_step != BookingStep.NOT_STARTED:
            response = booking_service.process_guided_booking_step("current", message)
            return ChatResponse(response=response)
        
        # Step 4: RAG processing (run async to avoid blocking)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, ask_question, message)
        
        # Log only slow responses
        elapsed = (datetime.now() - start_time).total_seconds()
        if elapsed > 1.0:
            logger.info(f"Slow response: {elapsed:.2f}s")
        
        return ChatResponse(response=response)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return ChatResponse(response="I'm having technical issues. Please call +65 6311 2330.")

# ===============================
# ERROR HANDLERS
# ===============================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors"""
    logger.error(f"Internal error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# ===============================
# RUN SERVER
# ===============================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000, log_level="info")