"""
Helper formatting and utility functions
"""

import pandas as pd
from typing import Union

def format_currency(value: Union[int, float], currency: str = "₹") -> str:
    """Formats a number as Indian Rupee or standard currency string."""
    if pd.isna(value) or value is None:
        return f"{currency}0"
    
    val = float(value)
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    
    if abs_val >= 10_000_000:
        return f"{sign}{currency}{abs_val / 10_000_000:.2f} Cr"
    elif abs_val >= 100_000:
        return f"{sign}{currency}{abs_val / 100_000:.2f} Lakh"
    elif abs_val >= 1_000:
        return f"{sign}{currency}{abs_val:,.0f}"
    else:
        return f"{sign}{currency}{abs_val:.2f}"

def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """Formats float (e.g. 18.5) or decimal (0.185) as percentage."""
    if pd.isna(value) or value is None:
        return "0.0%"
    val = float(value)
    # If given as 0.15 instead of 15
    if 0 < val <= 1:
        val = val * 100
    return f"{val:.{decimal_places}f}%"

def format_number(value: Union[int, float]) -> str:
    """Formats count or integer with comma separators."""
    if pd.isna(value) or value is None:
        return "0"
    return f"{int(value):,}"
