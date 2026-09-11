"""
RAG Retriever Module
Provides high-level document ingestion and semantic query retrieval.
"""

from typing import List, Dict, Any, Union
from datetime import datetime
from pathlib import Path
import io

from rag.document_loader import extract_text_from_file, chunk_text
from rag.vector_store import get_vector_store
from utils.logging import logger

def ingest_document_file(file_source: Union[str, Path, io.BytesIO], filename: str) -> Dict[str, Any]:
    """
    Parses, chunks, and indexes a business document into the persistent vector store.
    """
    raw_text = extract_text_from_file(file_source, filename)
    if not raw_text.strip():
        return {
            "success": False,
            "filename": filename,
            "message": "No extractable text found in file."
        }
        
    chunks = chunk_text(raw_text, source_name=filename, chunk_size=350, chunk_overlap=80)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    store = get_vector_store()
    store.add_document(filename, chunks, timestamp)
    
    return {
        "success": True,
        "filename": filename,
        "chunk_count": len(chunks),
        "char_count": len(raw_text),
        "timestamp": timestamp,
        "message": f"Successfully indexed {filename} ({len(chunks)} chunks)."
    }

def retrieve_context(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieves top matching document passages for a query."""
    store = get_vector_store()
    return store.search(query, top_k=top_k)
