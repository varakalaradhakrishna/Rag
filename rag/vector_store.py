"""
Persistent Semantic Vector Store
Uses Scikit-Learn TF-IDF vector space embeddings with sublinear term-frequency scaling
and cosine similarity matching. Fully persistent, zero external C++ dependencies, 100% reliable.
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.config import BASE_DIR
from utils.logging import logger

VECTOR_DB_PATH = BASE_DIR / "rag" / "rag_knowledge.db"

class PersistentVectorStore:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or VECTOR_DB_PATH)
        self._init_db()
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.chunks: List[Dict[str, Any]] = []
        self._reload_index()
        
    def _init_db(self):
        """Initializes SQLite tables for RAG documents and chunks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_documents (
                doc_name TEXT PRIMARY KEY,
                upload_timestamp TEXT,
                chunk_count INTEGER,
                char_count INTEGER
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_chunks (
                chunk_id TEXT PRIMARY KEY,
                doc_name TEXT,
                chunk_text TEXT,
                word_count INTEGER,
                FOREIGN KEY (doc_name) REFERENCES rag_documents(doc_name)
            );
        """)
        conn.commit()
        conn.close()
        
    def _reload_index(self):
        """Loads all stored chunks and fits the TF-IDF vectorizer."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT chunk_id, doc_name, chunk_text, word_count FROM rag_chunks")
        rows = cursor.fetchall()
        conn.close()
        
        self.chunks = [
            {"chunk_id": r[0], "source": r[1], "text": r[2], "word_count": r[3]}
            for r in rows
        ]
        
        if self.chunks:
            corpus = [c["text"] for c in self.chunks]
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                stop_words="english"
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            logger.info(f"RAG Vector Store indexed {len(self.chunks)} chunks across {len(self.get_document_list())} documents.")
        else:
            self.vectorizer = None
            self.tfidf_matrix = None
            
    def add_document(self, doc_name: str, chunks: List[Dict[str, Any]], upload_timestamp: str):
        """
        Adds a new document and its chunks into the knowledge base.
        Preserves previously uploaded documents.
        """
        if not chunks:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert or replace doc entry
        total_chars = sum(len(c["text"]) for c in chunks)
        cursor.execute("""
            INSERT OR REPLACE INTO rag_documents (doc_name, upload_timestamp, chunk_count, char_count)
            VALUES (?, ?, ?, ?)
        """, (doc_name, upload_timestamp, len(chunks), total_chars))
        
        # Delete old chunks for this specific document if re-uploading
        cursor.execute("DELETE FROM rag_chunks WHERE doc_name = ?", (doc_name,))
        
        for c in chunks:
            cursor.execute("""
                INSERT OR REPLACE INTO rag_chunks (chunk_id, doc_name, chunk_text, word_count)
                VALUES (?, ?, ?, ?)
            """, (c["chunk_id"], doc_name, c["text"], c["word_count"]))
            
        conn.commit()
        conn.close()
        
        # Re-build vector index with accumulated chunks
        self._reload_index()
        logger.info(f"Successfully added document '{doc_name}' with {len(chunks)} chunks to RAG store.")
        
    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Performs semantic cosine similarity search against indexed business documents.
        """
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []
            
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Rank by score
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score > 0.05:  # Relevance threshold
                chunk = self.chunks[idx].copy()
                chunk["similarity_score"] = round(score, 3)
                results.append(chunk)
                
        return results

    def get_document_list(self) -> List[Dict[str, Any]]:
        """Lists all currently indexed documents."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT doc_name, upload_timestamp, chunk_count, char_count FROM rag_documents ORDER BY upload_timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {"doc_name": r[0], "upload_timestamp": r[1], "chunk_count": r[2], "char_count": r[3]}
            for r in rows
        ]

# Global singleton
_vector_store_instance: Optional[PersistentVectorStore] = None

def get_vector_store() -> PersistentVectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = PersistentVectorStore()
    return _vector_store_instance
