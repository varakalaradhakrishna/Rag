"""
File Ingestion and Loader Utility
Safely loads CSV and Excel (XLSX/XLS) datasets with fallback encodings.
"""

import io
from typing import Union, Tuple, Optional
import pandas as pd
from utils.logging import logger

def load_file_to_df(file_source: Union[str, io.BytesIO], filename: str) -> Tuple[Optional[pd.DataFrame], str]:
    """
    Reads CSV or Excel file into a pandas DataFrame.
    
    Returns:
        (df, message)
    """
    ext = filename.lower().split('.')[-1]
    
    try:
        if ext == 'csv':
            # Try utf-8 first, fallback to latin-1
            try:
                if isinstance(file_source, str):
                    df = pd.read_csv(file_source, encoding='utf-8')
                else:
                    file_source.seek(0)
                    df = pd.read_csv(file_source, encoding='utf-8')
            except UnicodeDecodeError:
                if isinstance(file_source, str):
                    df = pd.read_csv(file_source, encoding='latin-1')
                else:
                    file_source.seek(0)
                    df = pd.read_csv(file_source, encoding='latin-1')
            return df, "CSV file loaded successfully."
            
        elif ext in ['xlsx', 'xls']:
            if isinstance(file_source, str):
                df = pd.read_excel(file_source)
            else:
                file_source.seek(0)
                df = pd.read_excel(file_source)
            return df, "Excel file loaded successfully."
        else:
            return None, f"Unsupported file extension: .{ext}. Please upload a .csv or .xlsx file."
            
    except Exception as e:
        logger.error(f"Failed to load file {filename}: {e}")
        return None, f"Error reading file {filename}: {str(e)}"
