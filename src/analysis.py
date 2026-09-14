from __future__ import annotations

import pandas as pd


def missing_values_report(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build a missing-values summary."""
    return pd.DataFrame(
        {
            "missing_count": dataframe.isna().sum(),
            "missing_ratio": dataframe.isna().mean(),
        }
    ).sort_values("missing_count", ascending=False)
