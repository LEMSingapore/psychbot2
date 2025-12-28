# src/ingest.py
# Document ingestion script for the PsychBot RAG (Retrieval-Augmented Generation) system.
# This script processes text documents and converts them into searchable vector embeddings

import os
# LangChain imports for document processing and vector storage
from langchain_community.document_loaders import TextLoader  # Loads text files into LangChain document format
from langchain_text_splitters import RecursiveCharacterTextSplitter  # Splits large documents into smaller chunks
from langchain_huggingface import HuggingFaceEmbeddings  # Converts text to numerical vectors using HuggingFace models
from langchain_community.vectorstores import Chroma  # Vector database for storing and searching embeddings

# ===============================
# MAIN INGESTION FUNCTION
# ===============================

def ingest_data(data_dir="data", persist_dir="docs"):
    """
    Turn text documents into a searchable database for the chatbot.
    
    Process: load files → split into chunks → convert to vectors → save database
    """
    
    # STEP 1: Load all text files from folder
    print("📂 Loading documents from:", data_dir)
    documents = []
    
    for filename in os.listdir(data_dir):
        # Only process text and markdown files
        if filename.endswith(".txt") or filename.endswith(".md"):
            loader = TextLoader(os.path.join(data_dir, filename))
            documents.extend(loader.load())

    print(f"📄 Loaded {len(documents)} documents.")

    # STEP 2: Break documents into smaller pieces
    # Small chunks give better answers and fit AI model limits
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,    # Max characters per chunk
        chunk_overlap=50   # Overlap to keep context
    )
    chunks = splitter.split_documents(documents)
    print(f"✂️ Split into {len(chunks)} chunks.")

    # STEP 3: Set up model to convert text to vectors
    # Uses fast model that understands text meaning
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # STEP 4: Create searchable vector database
    # Stores chunks as vectors so chatbot can find relevant content
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_dir,
    )
    
    print("✅ Embeddings stored in:", persist_dir)

# ===============================
# SCRIPT EXECUTION
# ===============================

if __name__ == "__main__":
    """
    Run ingestion to build chatbot's knowledge base.
    Execute when adding new documents to data folder.
    """
    ingest_data()