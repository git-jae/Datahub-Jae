import pandas as pd
from db.mysql_connection import conectar_mysql


def consultar_telemarketing(lista_dados):
    if not lista_dados:
        return pd.DataFrame()

    conn = conectar_mysql()
    cursor = conn.cursor()
    placeholders = ",".join(["%s"] * len(lista_dados))
    query = f"""
        SELECT
            ip.NR_RASTREAMENTO AS NR_RASTREIO,
            c.CD_CLIENTE,
            c2.NM_CLIENTE AS NM_EMPRESA,
            c2.NR_DOCUMENTO AS DOC_EMPRESA,
            c2.NR_TELEFONE AS TEL_EMPRESA,
            c.NR_TELEFONE AS TEL_FUNC,
            c2.TX_EMAIL AS EMAIL_EMPRESA,
            c.NM_CLIENTE AS NM_DESTINATARIO,
            c.NR_DOCUMENTO AS DOC_FUNC,
            e_filtrado.TX_LOGRADOURO,
            e_filtrado.NR_LOGRADOURO,
            e_filtrado.TX_COMPLEMENTO_LOGRADOURO,
            e_filtrado.NM_BAIRRO,
            e_filtrado.NM_CIDADE
        FROM ITEM_PEDIDO ip
        LEFT JOIN CLIENTE c ON ip.CD_CLIENTE = c.CD_CLIENTE
        LEFT JOIN PEDIDO p ON ip.NR_PEDIDO = p.NR_PEDIDO
        LEFT JOIN CLIENTE c2 ON p.CD_CLIENTE = c2.CD_CLIENTE
        LEFT JOIN (
            SELECT
                ipe.NR_PEDIDO,
                ipe.TX_LOGRADOURO,
                ipe.NR_LOGRADOURO,
                ipe.TX_COMPLEMENTO_LOGRADOURO,
                ipe.NM_BAIRRO,
                ipe.NM_CIDADE,
                ROW_NUMBER() OVER (
                    PARTITION BY ipe.NR_PEDIDO
                    ORDER BY ipe.NR_ITEM_PEDIDO DESC
                ) as rank_endereco
            FROM ITEM_PEDIDO_ENDERECO ipe
        ) e_filtrado ON e_filtrado.NR_PEDIDO = ip.NR_PEDIDO AND e_filtrado.rank_endereco = 1
        WHERE ip.NR_RASTREAMENTO IN ({placeholders})
    """
    cursor.execute(query, lista_dados)
    dados = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return pd.DataFrame(dados, columns=colunas)
