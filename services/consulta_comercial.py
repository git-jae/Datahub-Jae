import pandas as pd
from psycopg2.extras import RealDictCursor
from db.mysql_connection import conectar_mysql
from db.postgres_connection import conectar_m_postgres, conectar_t_postgres


def consulta_banco_cliente(lista_documentos):
    if not lista_documentos:
        return pd.DataFrame()
    conn = conectar_mysql()
    cursor = conn.cursor(dictionary=True)
    placeholders = ",".join(["%s"] * len(lista_documentos))
    query = f"""
        SELECT NR_DOCUMENTO, CD_CLIENTE
        FROM principal_db.CLIENTE
        WHERE NR_DOCUMENTO IN ({placeholders})
    """
    cursor.execute(query, lista_documentos)
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(dados)


def consulta_banco_rastreio(lista_documentos):
    if not lista_documentos:
        return pd.DataFrame()
    conn = conectar_mysql()
    cursor = conn.cursor(dictionary=True)
    placeholders = ",".join(["%s"] * len(lista_documentos))
    query = f"""
        WITH pedidos AS (
        SELECT
            ip.ID_MIDIA AS ID_MIDIA_PEDIDO,
            c.CD_CLIENTE,
            c.NM_CLIENTE as NM_FUNC,
            ip.NR_RASTREAMENTO AS NR_RASTREIO,
            c2.NM_CLIENTE AS SOLICITANTE,
            c.NR_DOCUMENTO AS DOC_FUNC,
            ROW_NUMBER() OVER (PARTITION BY c.CD_CLIENTE ORDER BY ip.NR_ITEM_PEDIDO DESC) AS rn
        FROM ITEM_PEDIDO ip
        LEFT JOIN CLIENTE c ON ip.CD_CLIENTE = c.CD_CLIENTE
        LEFT JOIN PEDIDO p ON ip.NR_PEDIDO = p.NR_PEDIDO
        LEFT JOIN CLIENTE c2 ON p.CD_CLIENTE = c2.CD_CLIENTE
        WHERE ip.CD_TIPO_ITEM_PEDIDO IN (3, 5, 6, 8, 10)
          AND (ip.NR_RASTREAMENTO NOT LIKE '%GT%' AND ip.NR_RASTREAMENTO NOT LIKE '%GV%' AND ip.NR_RASTREAMENTO IS NOT NULL)
          AND c.NR_DOCUMENTO IN ({placeholders})
        )
    SELECT
    DOC_FUNC,
    NM_FUNC,
    NR_RASTREIO,
    SOLICITANTE,
    ID_MIDIA_PEDIDO
    FROM pedidos
    WHERE rn = 1  
    """
    cursor.execute(query, lista_documentos)
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(dados)


def consulta_banco_midia(ids_clientes):
    if not ids_clientes:
        return pd.DataFrame()
    conn = conectar_m_postgres()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    placeholders = ",".join(["%s"] * len(ids_clientes))
    query = f"""
        WITH ultimas_midias AS (
            SELECT
                mc.id_cliente,
                sm.descricao AS STATUS_MIDIA,
                ROW_NUMBER() OVER (PARTITION BY mc.id_cliente ORDER BY mc.dt_associacao DESC) AS rn
            FROM midia m
            INNER JOIN midia_cliente mc ON mc.id_midia = m.id
            LEFT JOIN status_midia sm ON sm.id = m.id_status_midia
            WHERE m.id_tipo_midia IN (1, 4) AND m.id_aplicacao IN (10, 30)
        )
        SELECT id_cliente, STATUS_MIDIA
        FROM ultimas_midias
        WHERE rn = 1 AND id_cliente IN ({placeholders})
    """
    cursor.execute(query, ids_clientes)
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(dados)


def consulta_banco_transacao(ids_clientes):
    if not ids_clientes:
        return pd.DataFrame()
    conn = conectar_t_postgres()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    placeholders = ",".join(["%s"] * len(ids_clientes))
    query = f"""
        SELECT t.id_cliente,
               COUNT(*) FILTER (WHERE t.id_tipo_midia = 2 AND t.data_transacao >= CURRENT_DATE - INTERVAL '365 days') AS QTD_TRANSACAO_QRCODE,
               COUNT(*) FILTER (WHERE t.id_tipo_midia IN (1, 4) AND t.data_transacao >= CURRENT_DATE - INTERVAL '90 days') AS QTD_TRANSACAO_CARTAO
        FROM transacao t
        WHERE t.id_cliente IN ({placeholders})
          AND t.veiculo_id <> 99999
          AND t.cd_aplicacao IN (30, 10)
        GROUP BY t.id_cliente
    """
    cursor.execute(query, ids_clientes)
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return pd.DataFrame(dados)


def consultar_comercial(lista_documentos):
    if not lista_documentos:
        return pd.DataFrame()

    df_base = pd.DataFrame(lista_documentos, columns=['CPF'])
    df_base['CPF'] = df_base['CPF'].astype(str).str.zfill(11)

    df_clientes = consulta_banco_cliente(lista_documentos)
    if not df_clientes.empty:
        df_clientes['NR_DOCUMENTO'] = df_clientes['NR_DOCUMENTO'].astype(str).str.zfill(11)

    df_rastreios = consulta_banco_rastreio(lista_documentos)
    if not df_rastreios.empty:
        df_rastreios['DOC_FUNC'] = df_rastreios['DOC_FUNC'].astype(str).str.zfill(11)

    ids_clientes = df_clientes['CD_CLIENTE'].dropna().unique().tolist() if not df_clientes.empty else []

    df_midias     = consulta_banco_midia(ids_clientes)
    df_transacoes = consulta_banco_transacao(ids_clientes)

    df_final = df_base.merge(df_clientes,  left_on='CPF', right_on='NR_DOCUMENTO', how='left')
    df_final = df_final.merge(df_rastreios, left_on='CPF', right_on='DOC_FUNC',     how='left')
    df_final = df_final.merge(df_midias,    left_on='CD_CLIENTE', right_on='id_cliente', how='left')
    df_final = df_final.merge(df_transacoes, left_on='CD_CLIENTE', right_on='id_cliente', how='left')

    drop = ['DOC_FUNC', 'NR_DOCUMENTO', 'id_cliente_x', 'id_cliente_y']
    df_final = df_final.drop(columns=[c for c in drop if c in df_final.columns])

    return df_final
