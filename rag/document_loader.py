"""
Document Ingestion and Parsing Module
Extracts text from PDF and TXT documents, chunks into semantic passages, and tracks metadata.
"""

import io
from pathlib import Path
from typing import List, Dict, Any, Union
from pypdf import PdfReader
from utils.logging import logger

def extract_text_from_file(file_source: Union[str, Path, io.BytesIO], filename: str) -> str:
    """Extracts raw text content from TXT or PDF files."""
    ext = filename.lower().split(".")[-1]
    text = ""
    
    try:
        if ext == "txt":
            if isinstance(file_source, (str, Path)):
                with open(file_source, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
            else:
                file_source.seek(0)
                text = file_source.read().decode("utf-8", errors="replace")
                
        elif ext == "pdf":
            reader = PdfReader(file_source)
            extracted_pages = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(f"--- Page {i+1} ---\n{page_text}")
            text = "\n\n".join(extracted_pages)
            
        else:
            logger.warning(f"Unsupported file format: {ext}")
            return ""
            
    except Exception as e:
        logger.error(f"Error parsing document {filename}: {e}")
        return ""
        
    return text.strip()

def chunk_text(
    text: str,
    source_name: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Splits text into overlapping semantic windows with metadata.
    """
    if not text:
        return []
        
    words = text.split()
    if len(words) <= chunk_size:
        return [{
            "chunk_id": f"{source_name}_chunk_0",
            "source": source_name,
            "text": text,
            "word_count": len(words)
        }]
        
    chunks = []
    step = chunk_size - chunk_overlap
    idx = 0
    
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        chunk_str = " ".join(chunk_words)
        if len(chunk_words) > 20:  # Ignore tiny trailing fragments
            chunks.append({
                "chunk_id": f"{source_name}_chunk_{idx}",
                "source": source_name,
                "text": chunk_str,
                "word_count": len(chunk_words)
            })
            idx += 1
            
    return chunks
