import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

def conectar_m_postgres():
    """Banco de Mídia"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_M_HOST"),
        port=int(os.getenv("POSTGRES_M_PORT", 5432)),
        user=os.getenv("POSTGRES_M_USER"),
        password=os.getenv("POSTGRES_M_PASSWORD"),
        dbname=os.getenv("POSTGRES_M_DB"),
        connect_timeout=10,
    )

def conectar_t_postgres():
    """Banco de Transação"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_T_HOST"),
        port=int(os.getenv("POSTGRES_T_PORT", 5432)),
        user=os.getenv("POSTGRES_T_USER"),
        password=os.getenv("POSTGRES_T_PASSWORD"),
        dbname=os.getenv("POSTGRES_T_DB"),
        connect_timeout=10,
    )
