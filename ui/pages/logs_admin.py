import io
import pandas as pd
import streamlit as st
from logs.log_reader import get_logs_df
from ui.ui_helpers import page_header, divider, _kpi_card, A, T1, T2, T3

def render(user: dict):
    page_header("📋", "Logs de Auditoria", "AUDIT TRAIL")
    df = get_logs_df(limit=1000)

    if df.empty:
        st.info("Nenhum log registrado ainda.")
        return

    c1, c2, c3 = st.columns(3)
    with c1: fu = st.selectbox("Usuário",   ["Todos"] + sorted(df["usuario"].unique().tolist()),   key="lu")
    with c2: fc = st.selectbox("Categoria", ["Todas"] + sorted(df["categoria"].unique().tolist()), key="lc")
    with c3: fs = st.selectbox("Status",    ["Todos"] + sorted(df["status"].unique().tolist()),    key="ls")

    fil = df.copy()
    if fu != "Todos": fil = fil[fil["usuario"]   == fu]
    if fc != "Todas": fil = fil[fil["categoria"] == fc]
    if fs != "Todos": fil = fil[fil["status"]    == fs]

    divider()
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(_kpi_card("Registros Filtrados", len(fil)), unsafe_allow_html=True)
    with c2:
        erros = len(fil[fil["status"]=="error"]) if not fil.empty else 0
        st.markdown(_kpi_card("Erros", erros, "#f47067"), unsafe_allow_html=True)
    with c3:
        total = int(fil["quantidade"].sum()) if not fil.empty else 0
        st.markdown(_kpi_card("Registros Retornados", f"{total:,}", A), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:Nunito,sans-serif;font-size:13px;font-weight:800;'
                f'color:{T2};text-transform:uppercase;letter-spacing:0.8px;margin-bottom:10px;">'
                f'Log Completo ({len(fil)} registros)</div>', unsafe_allow_html=True)

    display = fil.copy()
    display["timestamp"] = display["timestamp"].dt.strftime("%d/%m/%Y %H:%M:%S")
    display.columns = ["Data/Hora","Usuário","Categoria","Registros","Status","Detalhe"]
    st.dataframe(display, use_container_width=True, hide_index=True)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        display.to_excel(w, index=False, sheet_name="Logs")
    st.download_button("⬇ Exportar Logs", data=buf.getvalue(),
        file_name="auditoria_datahub.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
