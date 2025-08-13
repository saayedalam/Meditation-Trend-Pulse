# utils/data_loader.py
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st

# Fixed path: repo_root/data/streamlit
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "streamlit"


@st.cache_data(show_spinner=False)
def read_data_csv(filename: str, **kwargs) -> pd.DataFrame:
    """
    Load a CSV from the fixed data/streamlit folder with caching.
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"{path} not found.")
    return pd.read_csv(path, **kwargs)


def last_updated_str(filename: str, fmt: str = "%B %d, %Y") -> str:
    """
    Return formatted last-modified date for a CSV.
    """
    path = DATA_DIR / filename
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts).strftime(fmt)