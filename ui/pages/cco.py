import io
from datetime import datetime

import pandas as pd
import streamlit as st

from ui.ui_helpers import page_header, divider, show_result, info_box, BD, A, BG, T2
from utils.excel_reader import read_excel_column
from utils.input_parser import parse_text_input
from logs.auditoria_execucao import registrar
from services.consulta_cco import consultar_cco


# ── helpers ───────────────────────────────────────────────────────────────────

def _build_meta(lista_entrada: list, df: pd.DataFrame) -> dict:
    return {
        "total_entrada":   len(lista_entrada),
        "total_limpo":     len(lista_entrada),
        "total_resultado": len(df),
        "status":          "success" if not df.empty else "vazio",
    }


def _run_query(tipo: str, valores: list, user: dict):
    """Executa a consulta CCO e exibe o resultado."""
    if not valores:
        st.warning("Informe ao menos um valor.")
        return

    divider()
    with st.spinner("Consultando bases CCO…"):
        try:
            df   = consultar_cco(valores, tipo_consulta=tipo)
            meta = _build_meta(valores, df)
            registrar(
                user["username"],
                f"CCO-{'Lógico' if tipo == 'logico' else 'Físico'}",
                meta["total_resultado"],
                meta["status"],
            )
            show_result(df, "Consulta CCO", meta)
        except Exception as e:
            st.error(f"Erro na consulta: {e}")
            registrar(user["username"], "CCO", 0, "error", str(e))


# ── page ──────────────────────────────────────────────────────────────────────

def render(user: dict):
    page_header("💳", "Consulta CCO", "CARTÕES")

    info_box(
        "Informe os <strong style='color:#e8eaf2;'>números lógicos ou físicos</strong> "
        "dos cartões CCO via planilha ou digitação.<br>"
        f"Separe por <code style='background:{BD};padding:1px 6px;border-radius:4px;'>vírgula</code>, "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>enter</code> ou "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>espaço</code>."
    )

    # ── Tipo de número ────────────────────────────────────────────────────
    tipo_label = st.selectbox(
        "Tipo de número",
        ["Número Lógico", "Número Físico"],
        key="cco_tipo",
    )
    tipo = "logico" if tipo_label == "Número Lógico" else "fisico"

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Abas ──────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📁  Upload Excel", "⌨️  Digitação Manual"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        up = st.file_uploader(
            "Planilha Excel ou CSV",
            type=["xlsx", "xls", "csv"],
            key="cco_up",
        )
        if up:
            try:
                col  = st.text_input(
                    "Nome da coluna (vazio = primeira)",
                    key="cco_col",
                    placeholder="ex: nr_logico_midia",
                )
                vals = read_excel_column(up, column_name=col or None)
                st.success(f"✅ {len(vals)} valores lidos.")
                if st.button("▶  Executar Consulta", key="cco_ex"):
                    _run_query(tipo, vals, user)
            except Exception as e:
                st.error(str(e))

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        txt = st.text_area(
            "Números dos cartões",
            height=150,
            placeholder="123456789\n987654321\n\nou: 123456789, 987654321",
            key="cco_txt",
        )
        if st.button("▶  Executar Consulta", key="cco_mn"):
            _run_query(tipo, parse_text_input(txt), user)
