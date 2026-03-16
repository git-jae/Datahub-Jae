import pandas as pd
from utils.data_cleaner import clean_values

_MOCK = {
    "NF-12345":{"destinatario":"Alpha Distribuidora","transportadora":"Rapidex",  "rastreio":"RX000012345BR","data_emissao":"2024-03-01","previsao":"2024-03-06","status":"Entregue",          "cidade":"São Paulo - SP"},
    "NF-12346":{"destinatario":"Beta Comércio",      "transportadora":"LogBrasil","rastreio":"LB000098765BR","data_emissao":"2024-03-05","previsao":"2024-03-12","status":"Em trânsito",       "cidade":"Curitiba - PR"},
    "NF-12347":{"destinatario":"Gama Atacado",       "transportadora":"Rapidex",  "rastreio":"RX000054321BR","data_emissao":"2024-03-07","previsao":"2024-03-14","status":"Saiu para entrega", "cidade":"Recife - PE"},
    "NF-12348":{"destinatario":"Delta Varejo",       "transportadora":"TotalLog", "rastreio":"TL000011122BR","data_emissao":"2024-03-10","previsao":"2024-03-18","status":"Coletado",          "cidade":"Brasília - DF"},
    "NF-12349":{"destinatario":"Épsilon Tech",       "transportadora":"LogBrasil","rastreio":"LB000033344BR","data_emissao":"2024-03-12","previsao":"2024-03-20","status":"Aguardando coleta", "cidade":"Manaus - AM"},
}

def consultar_logistica(valores):
    rows = []
    for n in clean_values(valores):
        k = n.upper()
        rows.append({"nf":k,**(_MOCK[k] if k in _MOCK else
            {"destinatario":"Não encontrado","transportadora":"-","rastreio":"-","data_emissao":"-","previsao":"-","status":"-","cidade":"-"})})
    if not rows: return pd.DataFrame()
    df = pd.DataFrame(rows)
    df.columns = ["NF","Destinatário","Transportadora","Rastreio","Data Emissão","Previsão Entrega","Status","Cidade Destino"]
    return df
