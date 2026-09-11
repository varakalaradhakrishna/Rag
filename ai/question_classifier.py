"""
AI Question Classifier & Intent Router
Classifies questions into SQL (Structured Data), RAG (Business Docs), FORECAST (ML), or HYBRID.
"""

import re
from typing import Dict, Any

def classify_question(query: str) -> Dict[str, Any]:
    """
    Determines the execution path for a natural-language query.
    
    Returns:
        {
            "route": "SQL" | "RAG" | "FORECAST" | "HYBRID",
            "confidence": float,
            "reason": str
        }
    """
    q = query.lower().strip()
    
    # 1. Forecasting triggers
    forecast_keywords = [
        "forecast", "predict", "prediction", "future", "next month", "next 7 days",
        "next 30 days", "next 60 days", "next 90 days", "upcoming", "projected",
        "what will revenue be", "what will sales be", "expected revenue", "expected sales"
    ]
    is_forecast = any(k in q for k in forecast_keywords)
    
    # 2. Document/RAG triggers
    rag_keywords = [
        "policy", "sop", "document", "report say", "guideline", "strategy say",
        "return policy", "pricing strategy", "replacement policy", "rule", "terms",
        "executive report", "what does the report", "according to"
    ]
    is_rag = any(k in q for k in rag_keywords)
    
    # 3. SQL / Data triggers
    sql_keywords = [
        "total revenue", "highest revenue", "top product", "most sold", "units sold",
        "how many orders", "average order value", "aov", "profit margin", "which category",
        "which state", "which city", "return rate", "repeat customer", "discount percent",
        "compare", "performance", "best selling", "worst performing", "rating"
    ]
    is_sql = any(k in q for k in sql_keywords)
    
    # 4. Hybrid triggers (e.g. "why did sales decrease and what should we do?", "analyze returns with policy")
    hybrid_keywords = [
        "what should we do", "why did sales", "recommend", "how can we improve",
        "suggest", "explain the change", "based on sales and report", "combined"
    ]
    is_hybrid = any(k in q for k in hybrid_keywords) or (is_sql and is_rag)
    
    if is_hybrid:
        return {
            "route": "HYBRID",
            "confidence": 0.95,
            "reason": "Query requires structured sales metrics combined with business document guidelines and strategic recommendations."
        }
    elif is_forecast:
        return {
            "route": "FORECAST",
            "confidence": 0.92,
            "reason": "Query requests predictive estimation of future business trends using ML models."
        }
    elif is_rag:
        return {
            "route": "RAG",
            "confidence": 0.90,
            "reason": "Query targets qualitative business knowledge, policies, or market reports."
        }
    else:
        # Default to SQL for analytical and quantitative business questions
        return {
            "route": "SQL",
            "confidence": 0.88,
            "reason": "Query requires aggregated relational calculation from the sales database."
        }
