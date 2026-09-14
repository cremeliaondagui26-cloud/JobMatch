from __future__ import annotations

import pandas as pd


def drop_empty_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a copy without fully empty rows."""
    return dataframe.dropna(how="all").copy()


def normalize_text_columns(dataframe: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Trim and lowercase selected text columns when present."""
    cleaned = dataframe.copy()
    for column in columns:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].astype(str).str.strip().str.lower()
    return cleaned
