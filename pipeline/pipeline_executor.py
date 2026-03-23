import pandas as pd
from utils.data_cleaner import clean_values
from services.consulta_comercial import consultar_comercial
from services.consulta_telemarketing import consultar_telemarketing
from services.consulta_devolucao import consultar_devolucao
from services.consulta_logistica import consultar_logistica
    

def executar_pipeline(categoria, valores_brutos):
    valores = clean_values(valores_brutos)
    base = {"categoria": categoria, "total_entrada": len(valores_brutos),
            "total_limpo": len(valores), "total_resultado": 0, "status": "vazio"}

    if not valores:
        return pd.DataFrame(), base

    cat = categoria.strip()
    if   cat == "Comercial":                    df = consultar_comercial(valores)
    elif cat == "Telemarketing":                df = consultar_telemarketing(valores)
    elif cat in ("Devolução", "Devolucao"):     df = consultar_devolucao(valores)
    elif cat in ("Logística", "Logistica"):     df = consultar_logistica(valores)
    else:
        raise ValueError(f"Categoria desconhecida: {categoria}")

    return df, {**base, "total_resultado": len(df), "status": "success"}
