import pandas as pd
from psycopg2.extras import RealDictCursor
from db.postgres_connection import conectar_m_postgres
from db.mysql_connection import conectar_mysql


def consultar_cco(lista_valores: list, tipo_consulta: str = "logico") -> pd.DataFrame:
    """
    Consulta informações de cartão CCO no Postgres (mídias) e MySQL (clientes).

    Args:
        lista_valores:  lista de strings com os números lógicos ou físicos.
        tipo_consulta:  "logico"  → filtra por m.nr_logico_midia
                        "fisico"  → filtra por m.nr_fisico_midia
    """
    if not lista_valores:
        return pd.DataFrame()

    # ── 1. PostgreSQL — tabela de mídias ──────────────────────────────────
    coluna_filtro = (
        "m.nr_logico_midia" if tipo_consulta == "logico" else "m.nr_fisico_midia"
    )
    placeholders = ",".join(["%s"] * len(lista_valores))

    query_midia = f"""
        SELECT
            m.nr_logico_midia,
            m.nr_fisico_midia,
            sm.descricao            AS status_midia,
            mc.id_cliente,
            mc.dt_associacao,
            mc.dt_desassociacao,
            m.dt_cancelamento_logico,
            m.dt_cancelamento_fisico,
            mcm.descricao           AS motivo_cancelamento_midia
        FROM midia m
        LEFT JOIN status_midia           sm  ON sm.id  = m.id_status_midia
        LEFT JOIN motivo_cancelamento_midia mcm ON mcm.id = m.id_motivo_cancelamento_midia
        LEFT JOIN midia_cliente          mc  ON mc.id_midia = m.id
        WHERE {coluna_filtro} IN ({placeholders})
    """

    conn_pg = conectar_m_postgres()
    try:
        cursor = conn_pg.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query_midia, lista_valores)
        df_midia = pd.DataFrame(cursor.fetchall())
        cursor.close()
    finally:
        conn_pg.close()

    if df_midia.empty:
        return df_midia

    # ── 2. MySQL — dados do cliente ───────────────────────────────────────
    ids_clientes = df_midia["id_cliente"].dropna().unique().tolist()
    if not ids_clientes:
        return df_midia

    ids_clientes = [int(i) for i in ids_clientes]
    placeholders_my = ",".join(["%s"] * len(ids_clientes))

    query_cli = f"""
        SELECT CD_CLIENTE, NM_CLIENTE, NR_DOCUMENTO
        FROM CLIENTE
        WHERE CD_CLIENTE IN ({placeholders_my})
    """

    conn_my = conectar_mysql()
    try:
        cursor_my = conn_my.cursor(dictionary=True)
        cursor_my.execute(query_cli, ids_clientes)
        df_clientes = pd.DataFrame(cursor_my.fetchall())
        cursor_my.close()
    finally:
        conn_my.close()

    if df_clientes.empty:
        return df_midia

    df_final = df_midia.merge(
        df_clientes,
        left_on="id_cliente",
        right_on="CD_CLIENTE",
        how="left",
    ).drop(columns=["CD_CLIENTE"], errors="ignore")

    return df_final
