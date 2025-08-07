# src/ingest.py
# Document ingestion script for the PsychBot RAG (Retrieval-Augmented Generation) system
# This script processes text documents and converts them into searchable vector embeddings

import os
# LangChain imports for document processing and vector storage
from langchain_community.document_loaders import TextLoader  # Loads text files into LangChain document format
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Splits large documents into smaller chunks
from langchain_huggingface import HuggingFaceEmbeddings  # Converts text to numerical vectors using HuggingFace models
from langchain_community.vectorstores import Chroma  # Vector database for storing and searching embeddings

def ingest_data(data_dir="data", persist_dir="docs"):
    """
    Main function to process documents and create a searchable vector database
    
    Process:
    1. Load all text/markdown files from data directory
    2. Split documents into smaller chunks for better retrieval
    3. Convert chunks to vector embeddings using AI model
    4. Store embeddings in a persistent vector database
    """
    
    # STEP 1: Load all text documents from the specified directory
    print("📂 Loading documents from:", data_dir)
    documents = []
    
    # Iterate through all files in the data directory
    for filename in os.listdir(data_dir):
        # Only process text and markdown files (common documentation formats)
        if filename.endswith(".txt") or filename.endswith(".md"):
            # Create a TextLoader for each file and load its content
            loader = TextLoader(os.path.join(data_dir, filename))
            # Add all loaded documents to our collection
            documents.extend(loader.load())

    print(f"📄 Loaded {len(documents)} documents.")

    # STEP 2: Split large documents into smaller, manageable chunks
    # This is crucial for RAG systems because:
    # - Smaller chunks provide more precise context for questions
    # - AI models have token limits, so chunks must fit within those limits
    # - Better chunk granularity improves retrieval accuracy
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,    # Maximum characters per chunk (balance between context and precision)
        chunk_overlap=50   # Characters to overlap between chunks (prevents losing context at boundaries)
    )
    chunks = splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks.")

    # STEP 3: Create embeddings model
    # Embeddings convert text into numerical vectors that capture semantic meaning
    # "all-MiniLM-L6-v2" is a lightweight, efficient model good for semantic similarity
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # STEP 4: Create and persist the vector database
    # Chroma is a vector database that stores embeddings and enables similarity search
    # When a user asks a question, the system can find the most relevant chunks
    vectorstore = Chroma.from_documents(
        documents=chunks,           # The text chunks to embed and store
        embedding=embedding_model,  # The model to convert text to vectors
        persist_directory=persist_dir,  # Where to save the database on disk
    )
    
    print("✅ Embeddings stored in:", persist_dir)

# Script execution entry point
if __name__ == "__main__":
    """
    When this script is run directly (not imported), execute the ingestion process
    This creates the vector database that the chatbot will use to answer questions
    """
    ingest_data()