# 🛒 BBD E-Commerce Sales Intelligence, Forecasting & RAG AI Analyst Platform

> **An Enterprise-Grade, Python-Only Platform for E-Commerce Data Analytics, Multi-Horizon Time-Series Forecasting, Document RAG, and Grounded AI Business Intelligence.**

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%203-003B57.svg)](https://www.sqlite.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Charts-Plotly%20Interactive-3F4F75.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. 📌 Problem Statement & Context
During mega festive sales such as Big Billion Days (BBD), e-commerce platforms process millions of transactions across disparate categories (Mobiles, Electronics, Fashion, Appliances). Business analysts and category managers face critical bottlenecks:
1. **Data Fragmentation**: Sales data arrives in incremental batches across weeks and months. Naive ingestion overwrites historical trends or introduces duplicate orders.
2. **Margin Erosion & Return Blind Spots**: Deep price discounting often accelerates top-line Gross Merchandise Value (GMV) while destroying bottom-line operating margins and driving high reverse logistics returns.
3. **Qualitative Disconnect**: Important operating constraints (category return windows, discount floors, carrier SLAs) live in unstructured policy documents and PDFs, completely disconnected from structured transactional SQL databases.
4. **Hallucination in AI Assistants**: Generic LLMs hallucinate financial metrics and lack grounded access to database state.

---

## 2. 🎯 Project Objective
This platform delivers a **single unified public web application** built **100% in Python** that:
* Ingests, sanitizes, and cumulatively accumulates transactional sales data without historical data loss.
* Automatically audits batches, skips duplicates (`Order_ID`), and logs every ingestion event.
* Provides multi-dimensional analytical views across Sales, Products, RFM Customer Loyalty, Regional Geos, Discounts, and Returns.
* Employs machine learning time-series regressors (Random Forest, Gradient Boosting, Ridge) to forecast 7, 30, 60, and 90-day revenue and unit demand with confidence bands.
* Houses a persistent RAG knowledge base for business policies and market reports.
* Features a centralized **AI Data Analyst** with multi-intent classification (SQL vs RAG vs Forecasting vs Hybrid) that synthesizes grounded, non-hallucinated responses with verifiable data evidence.

---

## 3. 🏗️ System Architecture

```text
                         PUBLIC WEBSITE (ONE UNIFIED URL)
                                        │
                                 STREAMLIT UI
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
                              Persistent Vector Store
```

---

## 4. 🧰 Technology Stack

| Layer | Technologies Used | Purpose |
|---|---|---|
| **Web Interface** | Streamlit | Single public URL, reactive controls, interactive UI |
| **Data Engine** | Pandas, NumPy | Data cleaning, vector operations, transformations |
| **Relational Storage** | SQLite 3 | Persistent ACID storage, indexes, audit history |
| **Visualizations** | Plotly (Express & Graph Objects) | Dark-themed, interactive drill-down charts |
| **Machine Learning** | Scikit-Learn | Random Forest, Gradient Boosting, Ridge, Metrics |
| **Document RAG** | PyPDF, Scikit-Learn TF-IDF | Semantic search, chunking, persistent vector store |
| **AI Synthesis** | Built-in Grounded Engine + Groq/OpenAI API | Intent routing, evidence synthesis, recommendations |

---

## 5. 📂 Project Directory Structure

```text
BBD-Ecommerce-Analytics/
│
├── app.py                     # Main unified Streamlit application entrypoint
├── requirements.txt           # Clean production dependencies
├── README.md                  # Comprehensive platform documentation
├── test_suite.py              # Automated unit and integration test suite
├── .gitignore                 # Standard Python, DB, and environment ignores
├── .env.example               # Environment variables template
│
├── data/
│   ├── sample/
│   │   ├── bbd_initial_sales_dataset.csv       # 10,500 initial transactions
│   │   ├── bbd_batch2_october_sales.csv        # 3,000 new test records
│   │   └── bbd_batch3_with_duplicates.xlsx     # 1,500 records (500 duplicates)
│   ├── documents/
│   │   ├── bbd_pricing_and_discount_strategy.txt
│   │   ├── bbd_return_and_replacement_policy.txt
│   │   └── bbd_q3_q4_executive_market_report.txt
│   └── generate_datasets.py   # Deterministic dataset synthesis script
│
├── database/
│   ├── __init__.py
│   ├── schema.py              # SQL tables & indexes definition
│   ├── database.py            # SQLite connection, insertion, deduplication
│   ├── queries.py             # Reusable parameterized SQL analytical queries
│   └── seed.py                # Database initialization bootstrapper
│
├── data_processing/
│   ├── __init__.py
│   ├── loader.py              # Resilient CSV/XLSX reader with encodings
│   ├── cleaner.py             # Whitespace strip, bounds clipping, audit report
│   ├── validator.py           # Schema checker & missing column detector
│   └── feature_engineering.py # Temporal, margin, and order value features
│
├── analytics/
│   ├── __init__.py
│   ├── sales.py               # Time-series, brand, category, channel aggregations
│   ├── products.py            # Best/worst products, ratings, margin rankings
│   ├── customers.py           # Repeat rate, CLV, RFM segmentation
│   ├── regional.py            # State & city revenue and market share
│   ├── discounts.py           # Discount elasticity and margin erosion
│   └── returns.py             # Reverse logistics, return rate, GMV loss
│
├── forecasting/
│   ├── __init__.py
│   ├── train.py               # Lag features, rolling windows, model comparison
│   ├── predict.py             # 7/30/60/90-day forward projections & insights
│   └── evaluation.py          # MAE, RMSE, MAPE, R² metric calculations
│
├── rag/
│   ├── __init__.py
│   ├── document_loader.py     # PDF & TXT parser with sliding chunking
│   ├── vector_store.py        # Persistent vector store with cosine matching
│   ├── retriever.py           # High-level semantic context retriever
│   └── rag_pipeline.py        # Knowledge base seeder and query engine
│
├── ai/
│   ├── __init__.py
│   ├── question_classifier.py # Dynamic intent router (SQL, RAG, ML, Hybrid)
│   ├── sql_agent.py           # Safe analytical query translator & executor
│   ├── analyst.py             # Grounded response synthesizer
│   └── prompts.py             # System prompts and structured schemas
│
├── ui/
│   ├── __init__.py
│   ├── styles.py              # CSS styles, KPI card generator, badges
│   ├── home.py                # 🏠 Home view & executive highlights
│   ├── dashboard.py           # 📊 Executive cross-filtered dashboard
│   ├── sales_view.py          # 📈 Sales & monthly trends view
│   ├── products_view.py       # 📦 Product catalog analytics
│   ├── customers_view.py      # 👥 Customer analytics & RFM loyalty
│   ├── regional_view.py       # 🌎 Regional & city analytics
│   ├── discounts_view.py      # 💰 Profit & discount elasticity
│   ├── returns_view.py        # 🔄 Returns & reverse logistics
│   ├── forecasting_view.py    # 🔮 ML multi-horizon forecasting
│   ├── ai_view.py             # 🤖 Central AI Data Analyst
│   ├── rag_view.py            # 📚 RAG knowledge base & document manager
│   ├── upload_view.py         # 📤 New data upload & deduplication audit
│   ├── data_management_view.py# 🗄️ Database management & upload history
│   └── about_view.py          # ℹ️ About project & methodology
│
└── utils/
    ├── __init__.py
    ├── config.py              # Paths, settings, environment loader
    ├── logging.py             # Unified application logger
    └── helpers.py             # Currency & number formatters
```

---

## 6. 📊 Synthetic Dataset Notice
> **Notice**: The supplied e-commerce dataset is **synthetic demo data** generated with statistical realism to mirror Indian festive season e-commerce trends (categories, brands, pricing tiers, state/city hubs, payment gateways, and return behaviors). It does **NOT** represent actual private customer or transaction data from Flipkart or any corporate entity.

### Raw Data Columns (19 Fields):
`Order_ID`, `Order_Date`, `Customer_ID`, `Product_ID`, `Product_Name`, `Category`, `Brand`, `MRP`, `Discount_Percent`, `Sale_Price`, `Quantity`, `Revenue`, `Profit`, `State`, `City`, `Payment_Method`, `Rating`, `Delivery_Days`, `Return_Flag`.

### Engineered Analytical Features (12 Fields):
`Year`, `Month`, `Month_Name`, `Week`, `Day`, `Day_Name`, `Quarter`, `Revenue_Per_Item`, `Discount_Amount`, `Profit_Margin`, `Order_Value`, `Is_Returned`.

---

## 7. 🔄 Continuous Data Ingestion & Deduplication

The platform implements the core principle:
$$\text{OLD DATA} + \text{NEW DATA} = \text{COMPLETE DATA}$$

```
Uploaded CSV / XLSX
        ↓
Schema Validation (Required 19 columns)
        ↓
Data Cleaning (Whitespace, type casting, bounds sanitization)
        ↓
Deduplication Audit (Check existing Order_IDs in SQLite)
        ↓
Display Ingestion Audit Report (New vs Duplicate vs Invalid)
        ↓
User Confirmation
        ↓
Append New Unique Records & Log to upload_history
        ↓
Analytics & Forecasts Instantly Re-synchronize
```

* Duplicates are never silently inserted.
* Historical transactions are never dropped or overwritten.
* Complete upload history is recorded in `upload_history` with timestamps and row tallies.

---

## 8. 🔮 Machine Learning Demand & Revenue Forecasting

### Multi-Horizon Projections:
* **Next 7 Days**: Operational fulfillment run-rate.
* **Next 30 Days**: Monthly working capital planning.
* **Next 60 Days**: Bi-monthly inventory replenishment.
* **Next 90 Days**: Quarterly strategic budget forecast.

### Feature Engineering for Time-Series:
* Calendar cycles: Day of week, day of month, month, weekend indicator.
* Lag variables: $\text{lag}_1$, $\text{lag}_7$, $\text{lag}_{14}$.
* Rolling statistics: 7-day and 14-day rolling means.

### Model Benchmarks Evaluated:
1. **Gradient Boosting Regressor**
2. **Random Forest Regressor**
3. **Ridge Regression**

The pipeline evaluates all models on a chronological test split, reports **MAE**, **RMSE**, **MAPE**, and $R^2$, and retrains the winning algorithm on full historical data. Interactive Plotly charts overlay historical actuals, predicted forecast lines, and $\pm 1.2 \times \text{RMSE}$ confidence intervals.

---

## 9. 📚 RAG Knowledge Base & Business Documents

Unstructured corporate guidelines are parsed, chunked, and indexed into a persistent semantic vector store:
* **Supported Formats**: PDF, TXT.
* **Chunking Strategy**: Overlapping semantic windows (350 words, 80-word overlap) preserving source attribution.
* **Vector Engine**: TF-IDF sublinear vectorization with cosine similarity ranking. Operates 100% offline with zero binary dependencies.
* **Pre-Loaded Documents**:
  1. `bbd_pricing_and_discount_strategy.txt` (Margin floors, category discount ceilings)
  2. `bbd_return_and_replacement_policy.txt` (Category return windows, IMEI replacement rules)
  3. `bbd_q3_q4_executive_market_report.txt` (Regional penetration, festive performance analysis)

---

## 10. 🤖 Grounded AI Data Analyst

The AI Analyst is equipped with dynamic question routing:

```
                      User Question
                            │
               Intent Classifier / Router
         ┌──────────────────┼──────────────────┐
         │                  │                  │
      [SQL]               [RAG]           [FORECAST]
         │                  │                  │
    SQLite Query       Vector Search      ML Projections
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                        [HYBRID]
                            │
             Synthesized Grounded Response
        ┌───────────────────────────────────────┐
        │ 💡 Answer: Natural summary            │
        │ 📊 Data Evidence: Exact SQL metrics   │
        │ 🔍 Business Insight: Analytical root  │
        │ 🚀 Recommendation: Action items      │
        │ 📑 Sources: SQLite / Docs / ML Model  │
        └───────────────────────────────────────┘
```

### Supported Example Queries:
* **Sales Facts**: *"What is our total revenue and average order value?"*
* **Product Ranks**: *"Which category generated the highest revenue?"*, *"Which product sold the most?"*
* **Regional Insights**: *"Which state has the highest revenue and order count?"*
* **Forecasting**: *"What will revenue be next month?"*, *"What is the expected sales quantity for the next 30 days?"*
* **RAG Policies**: *"What does the return policy say about Mobiles?"*, *"What does the pricing report say about discount ceilings?"*
* **Strategic Hybrid**: *"Why did sales decrease and what should we do?"*, *"Analyze returns and suggest improvements using the uploaded report."*

---

## 11. 🚀 Quickstart Installation Guide

### Prerequisites
* Python 3.10 to 3.14 installed on your system.
* Git installed.

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/BBD-Ecommerce-Analytics.git
cd BBD-Ecommerce-Analytics
```

### Step 2: Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Application
```bash
streamlit run app.py
```
The application will launch immediately at: `http://localhost:8501`

---

## 12. 🧪 Automated Testing
Run the comprehensive test suite verifying cleaning, database persistence, deduplication, analytics, forecasting, RAG, and AI routing:
```bash
python test_suite.py
```
Expected output:
```text
Ran 6 tests in 0.264s
OK
```

---

## 13. ☁️ Public Deployment Guide (Streamlit Community Cloud)

1. Push this clean repository to GitHub:
   ```bash
   git add .
   git commit -m "Deploy production BBD E-Commerce Intelligence Platform"
   git push origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io/).
3. Sign in with your GitHub account.
4. Click **"Create app"** and select your repository.
5. Set:
   * **Main file path**: `app.py`
   * **Python version**: 3.11 or 3.12
6. *(Optional)* Add API keys in **Advanced settings $\rightarrow$ Secrets**:
   ```toml
   GROQ_API_KEY = "gsk_..."
   OPENAI_API_KEY = "sk-..."
   ```
7. Click **"Deploy!"**
Your single unified website will be live at a public URL:
`https://your-custom-name.streamlit.app`

---

## 14. 🎓 Academic & Placement Value
This project demonstrates competency across:
1. **Data Engineering**: Data cleaning, schema validation, type enforcement, feature engineering, and robust SQLite ingestion with index optimization.
2. **Business Intelligence**: KPI computation, channel performance, cross-filtering, and RFM loyalty segmentation.
3. **Applied Machine Learning**: Time-series lag generation, rolling statistics, cross-validated regression algorithms, and multi-horizon forecasting.
4. **Natural Language Processing & RAG**: Semantic document chunking, TF-IDF vector embeddings, cosine relevance matching, and persistent retrieval.
5. **Generative AI Systems**: Intent classification, tool use, prompt templates, and grounded multi-source answer synthesis.
6. **Full-Stack Python**: Modern Streamlit UX with custom CSS styling, Plotly interactivity, and production error handling.

---

## 15. 📄 License
This project is distributed under the MIT License. See `LICENSE` for more details.
