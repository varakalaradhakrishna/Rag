"""
RAG Knowledge Base & Document Management View
Upload enterprise PDF/TXT business documents, manage indexed chunks, and test semantic retrieval.
"""

import streamlit as st
import pandas as pd
from rag.vector_store import get_vector_store
from rag.retriever import ingest_document_file, retrieve_context
from utils.helpers import format_number

def render_rag_view():
    st.title("📚 RAG Knowledge Base & Document Repository")
    st.caption("Empower the AI Data Analyst with unstructured business documents (return policies, vendor contracts, executive market research).")
    
    store = get_vector_store()
    
    tab1, tab2 = st.tabs(["📤 Upload Documents", "🔍 Semantic Document Search"])
    
    with tab1:
        st.subheader("Ingest New Business Document")
        st.markdown("Upload official company guidelines, category strategy briefs, or festive market reports (`.pdf` or `.txt`).")
        
        uploaded_doc = st.file_uploader("Select PDF or TXT Document", type=["pdf", "txt"])
        
        if uploaded_doc is not None:
            if st.button("📥 Index Document into Vector Store", type="primary"):
                with st.spinner("Extracting text, computing semantic chunks, and indexing..."):
                    res = ingest_document_file(uploaded_doc, uploaded_doc.name)
                    
                if res["success"]:
                    st.success(f"✅ Document `{res['filename']}` successfully indexed! Created **{res['chunk_count']}** semantic chunks ({format_number(res['char_count'])} characters).")
                    st.rerun()
                else:
                    st.error(f"Failed to index document: {res['message']}")
                    
        st.markdown("---")
        st.subheader("📑 Currently Indexed Knowledge Documents")
        doc_list = store.get_document_list()
        
        if doc_list:
            doc_df = pd.DataFrame(doc_list)
            doc_df.columns = ["Document Name", "Upload Timestamp", "Semantic Chunks", "Character Count"]
            doc_df["Semantic Chunks"] = doc_df["Semantic Chunks"].apply(format_number)
            doc_df["Character Count"] = doc_df["Character Count"].apply(format_number)
            st.dataframe(doc_df, use_container_width=True)
        else:
            st.info("No documents currently indexed. Upload a file above to expand the knowledge base.")
            
    with tab2:
        st.subheader("Test Semantic Retrieval")
        st.caption("Verify how relevant passages are matched to queries using cosine similarity.")
        
        search_query = st.text_input("Enter a query to search indexed documents:", placeholder="e.g. return window for appliances or mobile IMEI")
        
        if search_query:
            chunks = retrieve_context(search_query, top_k=4)
            if chunks:
                st.success(f"Found {len(chunks)} relevant document passages:")
                for i, c in enumerate(chunks):
                    with st.expander(f"Passage {i+1} — {c['source']} (Similarity Score: {c.get('similarity_score', 0):.2f})", expanded=(i==0)):
                        st.markdown(c["text"])
            else:
                st.warning("No matching passages found above relevance threshold.")
