import pandas as pd
from logs.auditoria_execucao import listar_logs

def get_logs_df(limit=500):
    records = listar_logs(limit)
    if not records:
        return pd.DataFrame(columns=["timestamp","usuario","categoria","quantidade","status","detalhe"])
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp", ascending=False).reset_index(drop=True)

def get_summary_stats(df):
    if df.empty:
        return {"total":0,"registros_total":0,"por_categoria":{},"por_usuario":{}}
    return {"total": len(df), "registros_total": int(df["quantidade"].sum()),
            "por_categoria": df["categoria"].value_counts().to_dict(),
            "por_usuario":   df["usuario"].value_counts().to_dict()}
