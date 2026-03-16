import pandas as pd
from psycopg2.extras import RealDictCursor
from db.mysql_connection import conectar_mysql
from db.postgres_connection import conectar_m_postgres


def consulta_banco_a(lista_rastreios):
    if not lista_rastreios:
        return pd.DataFrame()
    conn = conectar_mysql()
    cursor = conn.cursor(dictionary=True)
    placeholders = ",".join(["%s"] * len(lista_rastreios))
    query = f"""
        SELECT
            ip.NR_RASTREAMENTO,
            ip.ID_MIDIA,
            c2.NM_CLIENTE as NM_EMPRESA,
            c2.NR_DOCUMENTO as DOC_EMPRESA,
            c2.NR_TELEFONE as TEL_EMPRESA,
            c.NR_TELEFONE as TEL_FUNC,
            c2.TX_EMAIL as EMAIL_EMPRESA,
            c.NM_CLIENTE as NM_FUNC,
            c.NR_DOCUMENTO as DOC_FUNC
        FROM ITEM_PEDIDO ip
        LEFT JOIN TIPO_ITEM_PEDIDO tip ON ip.ID_PRODUTO = tip.CD_TIPO_ITEM_PEDIDO
        LEFT JOIN CLIENTE c ON ip.CD_CLIENTE = c.CD_CLIENTE
        LEFT JOIN PEDIDO p ON ip.NR_PEDIDO = p.NR_PEDIDO
        LEFT JOIN CLIENTE c2 ON p.CD_CLIENTE = c2.CD_CLIENTE
        WHERE ip.NR_RASTREAMENTO IN ({placeholders})
    """
    cursor.execute(query, lista_rastreios)
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(dados)


def consulta_banco_b(lista_ids):
    if not lista_ids:
        return pd.DataFrame()
    conn = conectar_m_postgres()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    placeholders = ",".join(["%s"] * len(lista_ids))
    query = f"""
        SELECT m.id, sm.descricao
        FROM midia m
        LEFT JOIN midia_cliente mc ON m.id = mc.id_midia
        LEFT JOIN status_midia sm ON sm.id = m.id_status_midia
        WHERE m.id IN ({placeholders})
    """
    cursor.execute(query, lista_ids)
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(dados)


def consultar_devolucao(lista_dados):
    if not lista_dados:
        return pd.DataFrame()

    df_a = consulta_banco_a(lista_dados)
    if df_a.empty:
        return df_a

    lista_ids = df_a['ID_MIDIA'].dropna().unique().tolist()
    if not lista_ids:
        return df_a

    df_b = consulta_banco_b(lista_ids)

    # Deduplicação
    if not df_b.empty:
        df_b = df_b.sort_values("id").drop_duplicates(subset=["id"], keep="first")

    df_final = df_a.merge(df_b, left_on="ID_MIDIA", right_on="id", how="left")
    df_final = df_final.drop(columns=[c for c in ['id'] if c in df_final.columns])

    return df_final
