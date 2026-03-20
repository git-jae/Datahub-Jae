import sys
import os
import pandas as pd
from db.postgres_connection import conectar_t_postgres
from psycopg2.extras import RealDictCursor

def executar_pipeline(categoria, dado_entrada):
    # 1. Tratamento da entrada
    if isinstance(dado_entrada, list):
        num = str(dado_entrada[0])
    elif isinstance(dado_entrada, pd.DataFrame):
        num = str(dado_entrada.iloc[0, 0])
    else:
        num = str(dado_entrada)

    # 2. Execução Direta da Query (Sem depender de outros arquivos)
    conn = conectar_t_postgres()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT 
        CASE 
        WHEN count(distinct mc.id_cliente) > 1 then 'Cartão com mais de uma associação' else 'OK' end as associacao
    from midia m
    inner join midia_cliente mc on mc.id_midia = m.id
        where m.nr_logico_midia = %s
    """
    
    try:
        cursor.execute(query, (num.strip(),))
        res = cursor.fetchone()
        status = res['tipo_cartao'] if res else "Sem transações"
        
        # Retorna o DataFrame para o Streamlit
        return pd.DataFrame([{"Número Lógico": num, "Resultado": status}])
        
    except Exception as e:
        return pd.DataFrame([{"Número Lógico": num, "Resultado": f"Erro: {str(e)}"}])
    finally:
        cursor.close()
        conn.close()