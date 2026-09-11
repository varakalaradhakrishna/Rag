"""
About Project View
Comprehensive architectural, methodology, and placement competency documentation.
"""

import streamlit as st

def render_about_view():
    st.title("ℹ️ About BBD E-Commerce Sales Intelligence")
    st.caption("A production-quality undergraduate Data Analytics, AI/ML, and RAG placement showcase project.")
    
    st.markdown("""
    ### 🎯 Project Purpose & Placement Competency
    This platform demonstrates end-to-end fluency in modern data analytics, relational databases, applied machine learning,
    and retrieval-augmented generation (RAG) within a unified, production-ready Python web application.
    
    It models real-world enterprise workflows where sales data is continuously uploaded in batches, historical integrity is strictly preserved,
    business policies evolve in unstructured documents, and business leaders demand an AI analyst that delivers verified, non-hallucinated figures.
    
    ---
    
    ### 🏗️ Complete System Architecture
    ```text
                             PUBLIC WEBSITE (ONE URL)
                                        │
                                    STREAMLIT
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
          ANALYTICS                FORECASTING                AI ANALYST
              │                         │                         │
         Pandas + SQL               ML Models              Question Router
              │                         │                         │
              │                         │              ┌──────────┼──────────┐
              │                         │              │          │          │
              │                         │             SQL        RAG      Forecast
              │                         │              │          │          │
              └─────────────────────────┼──────────────┴──────────┴──────────┘
                                        │
                                  SQLITE DATABASE
                                        ↑
                                        │
                              📤 NEW DATA UPLOAD
                                        │
                            OLD DATA + NEW DATA = COMPLETE
                                        │
                                        ↓
                                 COMPLETE HISTORY
    
                              RAG KNOWLEDGE BASE
                                        ↑
                                        │
                                Business Documents
                                        │
                                        ↓
                                Persistent Vector DB
    ```
    
    ---
    
    ### 🛠️ Technology Stack
    * **Application & Web Framework**: Streamlit (Pure Python, single URL architecture).
    * **Data Processing & Analytics**: Pandas, NumPy, SQLite 3, SQL Window Functions.
    * **Data Visualizations**: Plotly Express & Plotly Graph Objects (dark theme interactive charts).
    * **Machine Learning**: Scikit-Learn (Random Forest, Gradient Boosting, Ridge Regression, Time-Series Lag & Rolling Windows).
    * **RAG & Vector Engine**: Persistent Scikit-Learn TF-IDF Sublinear Vector Store + Cosine Similarity matching (100% offline resilient).
    * **LLM Integration**: Grounded fact synthesis engine with optional OpenAI / Groq API support via environment variables or Streamlit secrets.
    * **Document Parsers**: PyPDF for PDF extraction, native UTF-8 file decoders.
    
    ---
    
    ### 📌 Key Engineering Highlights
    1. **Zero Data Loss Ingestion**: New datasets append seamlessly to historical records. The system detects and rejects duplicates via `Order_ID`.
    2. **Multi-Horizon Demand Projections**: Predicts 7, 30, 60, and 90-day future revenue and unit demand with error metrics (MAE, RMSE, MAPE, $R^2$).
    3. **Evidence-Grounded AI**: The AI analyst never invents financial figures. Numerical facts are computed directly from the SQLite database.
    4. **Deployment-Ready**: Designed for immediate deployment to Streamlit Community Cloud with a single public URL.
    """)
