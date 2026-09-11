"""
Central AI Data Analyst Orchestrator
Coordinates intent classification, SQL ground-truth extraction, RAG semantic retrieval,
time-series forecasting, and optional LLM synthesis.
"""

import os
import requests
from typing import Dict, Any, Optional

from ai.question_classifier import classify_question
from ai.sql_agent import execute_safe_analytical_query
from ai.prompts import SYSTEM_ANALYST_PROMPT, FALLBACK_TEMPLATE
from rag.rag_pipeline import query_rag_knowledge
from forecasting.predict import generate_multi_horizon_forecast
from database.database import query_sales_df
from utils.config import OPENAI_API_KEY, GROQ_API_KEY, GEMINI_API_KEY
from utils.logging import logger
from utils.helpers import format_currency, format_number, format_percentage

def call_optional_llm(prompt_payload: str, api_key: str = "", provider: str = "auto") -> Optional[str]:
    """
    Calls configured LLM API (Groq / OpenAI / Gemini) if available.
    Returns None if no API key or network error, triggering instant smart fallback.
    """
    key = api_key or GROQ_API_KEY or OPENAI_API_KEY
    if not key:
        return None
        
    try:
        # If Groq key is detected (starts with gsk_ or specified)
        if (key.startswith("gsk_") or provider == "groq") and (GROQ_API_KEY or key):
            active_key = GROQ_API_KEY or key
            headers = {
                "Authorization": f"Bearer {active_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_ANALYST_PROMPT},
                    {"role": "user", "content": prompt_payload}
                ],
                "temperature": 0.2
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=12)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
                
        # If OpenAI key is detected (starts with sk-)
        elif key.startswith("sk-") or provider == "openai":
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_ANALYST_PROMPT},
                    {"role": "user", "content": prompt_payload}
                ],
                "temperature": 0.2
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=12)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
                
    except Exception as e:
        logger.warning(f"External LLM call skipped or failed ({e}). Using grounded analyst engine.")
        
    return None

def analyze_user_query(query: str, custom_api_key: str = "") -> Dict[str, Any]:
    """
    End-to-end question answering pipeline with multi-source synthesis.
    """
    classification = classify_question(query)
    route = classification["route"]
    
    # 1. SQL Route (Structured Database Facts)
    if route == "SQL":
        sql_res = execute_safe_analytical_query(query)
        evidence_list = "\n".join([f"• **{k}**: {v}" for k, v in sql_res["evidence"].items()])
        
        answer = sql_res["summary"]
        insight = "Performance trends align with customer category affinity and seasonal promotional participation."
        recommendation = "Maintain stock availability for high-velocity SKUs and monitor margin erosion from deep discounting."
        sources = "Sales Database (SQLite)"
        
        # Optional LLM polish
        llm_input = f"User Question: {query}\nSQL Evidence:\n{evidence_list}\nGenerate a crisp 4-part analyst summary."
        llm_output = call_optional_llm(llm_input, api_key=custom_api_key)
        
        final_text = llm_output if llm_output else FALLBACK_TEMPLATE.format(
            answer=answer,
            evidence=evidence_list,
            insight=insight,
            recommendation=recommendation,
            sources=sources
        )
        
        return {
            "route": route,
            "response": final_text,
            "evidence": sql_res["evidence"],
            "raw_data": sql_res.get("df"),
            "sources": [sources]
        }
        
    # 2. RAG Route (Qualitative Document Retrieval)
    elif route == "RAG":
        rag_res = query_rag_knowledge(query, top_k=3)
        if not rag_res["found"]:
            return {
                "route": route,
                "response": "No matching business documents or policies found in the RAG knowledge base for this query. Please upload relevant policy or report documents under the 'RAG Knowledge Base' page.",
                "evidence": {},
                "sources": []
            }
            
        sources_str = ", ".join(rag_res["sources"])
        context_snippets = rag_res["combined_context"]
        
        answer = f"Based on the official uploaded business documentation ({sources_str}), specific operational guidelines govern this policy."
        evidence = f"Relevant excerpts:\n\n{context_snippets[:600]}..."
        insight = "Documented standard operating procedures ensure operational compliance and protect gross margins."
        recommendation = "Adhere strictly to verified category return windows and promotional discount ceilings."
        
        llm_input = f"User Question: {query}\nDocument Context:\n{context_snippets}\nSynthesize an accurate answer based ONLY on the context."
        llm_output = call_optional_llm(llm_input, api_key=custom_api_key)
        
        final_text = llm_output if llm_output else FALLBACK_TEMPLATE.format(
            answer=answer,
            evidence=evidence,
            insight=insight,
            recommendation=recommendation,
            sources=f"Uploaded Business Documents ({sources_str})"
        )
        
        return {
            "route": route,
            "response": final_text,
            "evidence": {"Retrieved Chunks": len(rag_res["chunks"]), "Document Sources": sources_str},
            "sources": rag_res["sources"]
        }
        
    # 3. FORECAST Route (Predictive ML Projections)
    elif route == "FORECAST":
        df = query_sales_df("SELECT * FROM sales")
        target = "quantity" if "quantity" in query.lower() or "units" in query.lower() else "revenue"
        fc_res = generate_multi_horizon_forecast(df, target_col=target)
        
        if not fc_res.get("success"):
            return {
                "route": route,
                "response": fc_res.get("message", "Unable to compute forecast."),
                "evidence": {},
                "sources": ["Forecasting Engine"]
            }
            
        h30 = fc_res["horizon_summaries"].get("30_days", {})
        h7 = fc_res["horizon_summaries"].get("7_days", {})
        
        val_30 = format_currency(h30.get("total_forecast", 0)) if target == "revenue" else format_number(h30.get("total_forecast", 0))
        val_7 = format_currency(h7.get("total_forecast", 0)) if target == "revenue" else format_number(h7.get("total_forecast", 0))
        
        evidence_dict = {
            f"Next 7-Day Projected {target.capitalize()}": val_7,
            f"Next 30-Day Projected {target.capitalize()}": val_30,
            "Model Architecture": fc_res["model_name"],
            "Validation RMSE": f"{fc_res['metrics']['RMSE']:,}",
            "30-Day Trend Shift": f"{h30.get('trend_change_pct', 0):+.1f}% vs baseline"
        }
        evidence_list = "\n".join([f"• **{k}**: {v}" for k, v in evidence_dict.items()])
        
        answer = f"The machine learning model projects a total **{target}** of **{val_30}** over the next 30 days (run rate: **{val_7}** in next 7 days)."
        insight = "\n".join(fc_res["insights"])
        recommendation = "Adjust fulfillment center replenishment cycles to match forecasted velocity."
        sources = f"Machine Learning Time-Series Model ({fc_res['model_name']})"
        
        final_text = FALLBACK_TEMPLATE.format(
            answer=answer,
            evidence=evidence_list,
            insight=insight,
            recommendation=recommendation,
            sources=sources
        )
        
        return {
            "route": route,
            "response": final_text,
            "evidence": evidence_dict,
            "sources": [sources]
        }
        
    # 4. HYBRID Route (Structured Data + RAG Documents + Strategic Recommendations)
    else:
        sql_res = execute_safe_analytical_query(query)
        rag_res = query_rag_knowledge(query, top_k=2)
        
        evidence_lines = [f"• **{k}**: {v}" for k, v in sql_res["evidence"].items()]
        evidence_list = "\n".join(evidence_lines)
        
        doc_context = rag_res["combined_context"] if rag_res["found"] else "No specific policy document directly referenced."
        sources_list = ["Sales Database (SQLite)"]
        if rag_res["found"]:
            sources_list.extend(rag_res["sources"])
            
        answer = f"Cross-referencing real transaction records with our strategic business documents provides clear root-cause context."
        evidence = f"{evidence_list}\n\n**Business Knowledge Excerpt**:\n{doc_context[:450]}..."
        insight = "High sales volumes during discount spikes often mask return velocity and margin compression."
        recommendation = "1. Rebalance discounts to protect minimum margin floors.\n2. Implement pre-dispatch sizing prompts for apparel to curb return rates."
        sources_str = " + ".join(sources_list)
        
        llm_input = f"User Question: {query}\nStructured Evidence:\n{evidence_list}\nBusiness Context:\n{doc_context}\nProvide an executive hybrid answer."
        llm_output = call_optional_llm(llm_input, api_key=custom_api_key)
        
        final_text = llm_output if llm_output else FALLBACK_TEMPLATE.format(
            answer=answer,
            evidence=evidence,
            insight=insight,
            recommendation=recommendation,
            sources=sources_str
        )
        
        return {
            "route": "HYBRID",
            "response": final_text,
            "evidence": sql_res["evidence"],
            "sources": sources_list
        }
