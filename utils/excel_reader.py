import pandas as pd
from typing import Optional

def read_excel_column(file, column_index: int = 0, column_name: Optional[str] = None) -> list:
    name = getattr(file, "name", "")
    df = pd.read_csv(file, dtype=str) if name.endswith(".csv") else pd.read_excel(file, dtype=str)
    if column_name and column_name in df.columns:
        vals = df[column_name].dropna().tolist()
    elif df.shape[1] > column_index:
        vals = df.iloc[:, column_index].dropna().tolist()
    else:
        vals = []
    return [str(v).strip() for v in vals if str(v).strip()]
