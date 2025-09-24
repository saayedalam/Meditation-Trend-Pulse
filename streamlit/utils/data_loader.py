# Purpose: Read-only, cached CSV loading utilities for the Streamlit app.
# - Preserve existing behavior and signatures (no breaking changes).
# - Keep it simple, explicit, and readable (Zen of Python).

from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

# Fixed path: repo_root/data/streamlit
DATA_DIR: Path = Path(__file__).resolve().parents[2] / "data" / "streamlit"


@st.cache_data(show_spinner=False)
def read_data_csv(filename: str, **kwargs) -> pd.DataFrame:
    """
    Load a CSV from the fixed `data/streamlit` directory, with Streamlit caching.

    Parameters
    ----------
    filename
        Name of the CSV file relative to `data/streamlit` (e.g., 'global_trend_summary.csv').
    **kwargs
        Additional keyword arguments passed to `pandas.read_csv`.

    Returns
    -------
    pd.DataFrame
        The loaded dataset.

    Raises
    ------
    FileNotFoundError
        If the target CSV file does not exist.
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    return pd.read_csv(path, **kwargs)


def last_updated_str(filename: str, fmt: str = "%B %d, %Y") -> str:
    """
    Get the last-modified timestamp of a CSV in `data/streamlit`, formatted as text.

    Parameters
    ----------
    filename
        Name of the CSV file relative to `data/streamlit`.
    fmt
        Datetime format string for presentation (default: '%B %d, %Y').

    Returns
    -------
    str
        Formatted last-modified date (local time).

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts).strftime(fmt)