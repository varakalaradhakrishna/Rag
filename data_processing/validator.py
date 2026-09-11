"""
Dataset Schema and Quality Validator
Verifies presence of required columns, schema conformity, and data integrity.
"""

from typing import Dict, Any, Tuple
import pandas as pd
from utils.config import REQUIRED_COLUMNS

def validate_dataset_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validates uploaded DataFrame structure against expected schema.
    
    Returns validation report dictionary.
    """
    if df is None or df.empty:
        return {
            "is_valid": False,
            "total_rows": 0,
            "missing_columns": REQUIRED_COLUMNS,
            "extra_columns": [],
            "message": "Uploaded dataset is empty or corrupted."
        }
    
    df_cols = list(df.columns)
    df_cols_lower = [c.lower() for c in df_cols]
    col_mapping = {c.lower(): c for c in df_cols}
    
    missing_cols = []
    for req in REQUIRED_COLUMNS:
        if req.lower() not in df_cols_lower:
            missing_cols.append(req)
            
    is_valid = len(missing_cols) == 0
    
    extra_cols = [c for c in df_cols if c.lower() not in [r.lower() for r in REQUIRED_COLUMNS]]
    
    return {
        "is_valid": is_valid,
        "total_rows": len(df),
        "total_columns": len(df_cols),
        "present_columns": df_cols,
        "missing_columns": missing_cols,
        "extra_columns": extra_cols,
        "message": "Validation passed." if is_valid else f"Missing required columns: {', '.join(missing_cols)}"
    }
