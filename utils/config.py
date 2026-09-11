"""
Application Configuration Module
BBD E-Commerce Sales Intelligence & AI Data Analyst
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
DOCUMENTS_DIR = DATA_DIR / "documents"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "ecommerce_sales.db"
CHROMA_PERSIST_DIR = BASE_DIR / "rag" / "chroma_db"

# Ensure essential directories exist
for p in [DATA_DIR, SAMPLE_DATA_DIR, DOCUMENTS_DIR, DATABASE_DIR, CHROMA_PERSIST_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Load environment variables (.env file)
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

# Core App Configurations
APP_NAME = "BBD E-Commerce Sales Intelligence & AI Data Analyst"
APP_TAGLINE = "End-to-End Enterprise Analytics, ML Forecasting & Grounded RAG AI Platform"
APP_VERSION = "2.0.0"

# Target Columns for Ingestion
REQUIRED_COLUMNS = [
    "Order_ID",
    "Order_Date",
    "Customer_ID",
    "Product_ID",
    "Product_Name",
    "Category",
    "Brand",
    "MRP",
    "Discount_Percent",
    "Sale_Price",
    "Quantity",
    "Revenue",
    "Profit",
    "State",
    "City",
    "Payment_Method",
    "Rating",
    "Delivery_Days",
    "Return_Flag"
]

# LLM API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PREFERRED_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto")
