"""
RAG Pipeline Manager
Orchestrates initial knowledge base seeding and document retrieval synthesis.
"""

from pathlib import Path
from typing import Dict, Any, List
from utils.config import DOCUMENTS_DIR
from utils.logging import logger
from rag.retriever import ingest_document_file, retrieve_context
from rag.vector_store import get_vector_store

def seed_initial_documents_if_empty():
    """Indexes initial business reports if the RAG store is empty."""
    store = get_vector_store()
    docs = store.get_document_list()
    
    if len(docs) == 0:
        logger.info("RAG store empty. Seeding initial business documents...")
        if DOCUMENTS_DIR.exists():
            for doc_path in DOCUMENTS_DIR.glob("*.txt"):
                res = ingest_document_file(doc_path, doc_path.name)
                logger.info(f"Seeded doc: {doc_path.name} -> {res.get('message')}")
    else:
        logger.info(f"RAG store already contains {len(docs)} documents.")

def query_rag_knowledge(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Retrieves relevant business knowledge chunks for an input query.
    """
    chunks = retrieve_context(query, top_k=top_k)
    
    if not chunks:
        return {
            "found": False,
            "query": query,
            "chunks": [],
            "combined_context": "No relevant business policy or report passages found for this query.",
            "sources": []
        }
        
    combined_context = "\n\n".join([
        f"[Source: {c['source']} (Relevance: {c.get('similarity_score', 0):.2f})]\n{c['text']}"
        for c in chunks
    ])
    
    sources = list({c["source"] for c in chunks})
    
    return {
        "found": True,
        "query": query,
        "chunks": chunks,
        "combined_context": combined_context,
        "sources": sources
    }
