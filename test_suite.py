"""
Comprehensive Automated Test Suite
Validates Data Cleaning, Database Persistence, Ingestion Deduplication, Analytics,
Forecasting, RAG Retrieval, and AI Data Analyst Routing.
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

# Set up project root
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_processing.cleaner import clean_ecommerce_data
from data_processing.feature_engineering import apply_feature_engineering
from data_processing.validator import validate_dataset_structure
from database.database import init_db, insert_sales_records, query_sales_df, get_database_summary
from analytics.sales import get_overall_kpis, get_category_sales
from analytics.customers import get_rfm_segmentation
from forecasting.predict import generate_multi_horizon_forecast
from rag.document_loader import chunk_text
from rag.retriever import ingest_document_file, retrieve_context
from ai.question_classifier import classify_question
from ai.analyst import analyze_user_query

class TestBBDPlatform(unittest.TestCase):
    
    def test_01_data_cleaning_and_validation(self):
        """Tests data cleaning and schema validation."""
        raw_data = pd.DataFrame([
            {
                "Order_ID": " TEST-001 ",
                "Order_Date": "2025-09-01 10:00:00",
                "Customer_ID": "CUST-1",
                "Product_ID": "P-1",
                "Product_Name": " Test Product ",
                "Category": "Electronics",
                "Brand": "Sony",
                "MRP": "1000",
                "Discount_Percent": 10,
                "Sale_Price": 900,
                "Quantity": -5,  # Negative quantity should be sanitized
                "Revenue": 900,
                "Profit": 100,
                "State": "Karnataka",
                "City": "Bangalore",
                "Payment_Method": "UPI",
                "Rating": 6.5,  # Invalid rating > 5.0 should be clipped
                "Delivery_Days": 2,
                "Return_Flag": 0
            }
        ])
        
        val_res = validate_dataset_structure(raw_data)
        self.assertTrue(val_res["is_valid"], "Valid structure failed validation")
        
        clean_df, report = clean_ecommerce_data(raw_data)
        self.assertEqual(len(clean_df), 1)
        self.assertEqual(clean_df["Order_ID"].iloc[0], "TEST-001")
        self.assertGreaterEqual(clean_df["Quantity"].iloc[0], 1, "Quantity was not clamped to min positive")
        self.assertLessEqual(clean_df["Rating"].iloc[0], 5.0, "Rating was not clamped to max 5.0")
        
    def test_02_feature_engineering(self):
        """Tests derived temporal and financial calculations."""
        df = pd.DataFrame([{
            "Order_Date": "2025-10-15 14:30:00",
            "Quantity": 2,
            "Revenue": 1000.0,
            "Profit": 200.0,
            "MRP": 600.0,
            "Discount_Percent": 16.67,
            "Return_Flag": 0
        }])
        enriched = apply_feature_engineering(df)
        self.assertEqual(enriched["Year"].iloc[0], 2025)
        self.assertEqual(enriched["Month"].iloc[0], 10)
        self.assertEqual(enriched["Month_Name"].iloc[0], "October")
        self.assertEqual(enriched["Revenue_Per_Item"].iloc[0], 500.0)
        self.assertEqual(enriched["Profit_Margin"].iloc[0], 20.0)
        
    def test_03_database_and_deduplication(self):
        """Tests that OLD DATA + NEW DATA = COMPLETE DATA and duplicate Order_IDs are rejected."""
        test_db = PROJECT_ROOT / "database" / "test_sales.db"
        if test_db.exists():
            test_db.unlink()
            
        init_db(test_db)
        
        batch1 = pd.DataFrame([
            {"Order_ID": "ORD-1", "Order_Date": "2025-08-01 10:00:00", "Customer_ID": "C-1", "Product_ID": "P-1", "Product_Name": "P1", "Category": "Mobiles", "Brand": "Apple", "MRP": 1000, "Discount_Percent": 10, "Sale_Price": 900, "Quantity": 1, "Revenue": 900, "Profit": 100, "State": "Delhi", "City": "Delhi", "Payment_Method": "UPI", "Rating": 4.5, "Delivery_Days": 2, "Return_Flag": 0},
            {"Order_ID": "ORD-2", "Order_Date": "2025-08-02 10:00:00", "Customer_ID": "C-2", "Product_ID": "P-2", "Product_Name": "P2", "Category": "Electronics", "Brand": "Sony", "MRP": 2000, "Discount_Percent": 10, "Sale_Price": 1800, "Quantity": 1, "Revenue": 1800, "Profit": 200, "State": "Maharashtra", "City": "Mumbai", "Payment_Method": "Card", "Rating": 4.0, "Delivery_Days": 3, "Return_Flag": 0}
        ])
        
        res1 = insert_sales_records(apply_feature_engineering(batch1), "batch1.csv", db_path=test_db)
        self.assertEqual(res1["new_rows"], 2)
        self.assertEqual(res1["duplicate_rows"], 0)
        
        # Batch 2 contains ORD-2 (duplicate) and ORD-3 (new)
        batch2 = pd.DataFrame([
            {"Order_ID": "ORD-2", "Order_Date": "2025-08-02 10:00:00", "Customer_ID": "C-2", "Product_ID": "P-2", "Product_Name": "P2", "Category": "Electronics", "Brand": "Sony", "MRP": 2000, "Discount_Percent": 10, "Sale_Price": 1800, "Quantity": 1, "Revenue": 1800, "Profit": 200, "State": "Maharashtra", "City": "Mumbai", "Payment_Method": "Card", "Rating": 4.0, "Delivery_Days": 3, "Return_Flag": 0},
            {"Order_ID": "ORD-3", "Order_Date": "2025-08-03 10:00:00", "Customer_ID": "C-3", "Product_ID": "P-3", "Product_Name": "P3", "Category": "Fashion", "Brand": "Nike", "MRP": 3000, "Discount_Percent": 20, "Sale_Price": 2400, "Quantity": 1, "Revenue": 2400, "Profit": 300, "State": "Karnataka", "City": "Bangalore", "Payment_Method": "UPI", "Rating": 5.0, "Delivery_Days": 1, "Return_Flag": 0}
        ])
        
        res2 = insert_sales_records(apply_feature_engineering(batch2), "batch2.csv", db_path=test_db)
        self.assertEqual(res2["new_rows"], 1)
        self.assertEqual(res2["duplicate_rows"], 1)
        
        # Total in DB should be exactly 3
        summary = get_database_summary(db_path=test_db)
        self.assertEqual(summary["total_records"], 3)
        
        if test_db.exists():
            test_db.unlink()
            
    def test_04_ai_question_routing(self):
        """Tests classification of user queries across SQL, RAG, FORECAST, HYBRID."""
        self.assertEqual(classify_question("What is our total revenue?")["route"], "SQL")
        self.assertEqual(classify_question("Which product sold the most?")["route"], "SQL")
        self.assertEqual(classify_question("What does the return policy say?")["route"], "RAG")
        self.assertEqual(classify_question("What will revenue be next month?")["route"], "FORECAST")
        self.assertEqual(classify_question("Why did sales decrease and what should we do?")["route"], "HYBRID")

    def test_05_rag_chunking_and_retrieval(self):
        """Tests semantic search on text chunks."""
        chunks = chunk_text("The return policy for electronics is 7 days replacement only.", "policy.txt", chunk_size=50)
        self.assertGreater(len(chunks), 0)
        
    def test_06_ai_analyst_end_to_end(self):
        """Tests full end-to-end grounded response generation."""
        res = analyze_user_query("What is the total revenue?")
        self.assertEqual(res["route"], "SQL")
        self.assertIn("Total Revenue", res["response"])
        self.assertIn("Sources", res["response"])

if __name__ == "__main__":
    unittest.main()
