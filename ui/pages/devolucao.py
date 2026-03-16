import streamlit as st
from ui.ui_helpers import page_header, divider, show_result, info_box, BD
from utils.excel_reader import read_excel_column
from utils.input_parser import parse_text_input
from pipeline.pipeline_executor import executar_pipeline
from logs.auditoria_execucao import registrar

def render(user: dict):
    page_header("↩️", "Consulta Devolução", "RETURNS")
    info_box(
        f"Informe os <strong style='color:#e8eaf2;'>códigos de devolução</strong> (ex: DEV-001).<br>"
        f"Separe por <code style='background:{BD};padding:1px 6px;border-radius:4px;'>vírgula</code>, "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>enter</code> ou "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>espaço</code>.")

    tab1, tab2 = st.tabs(["📁  Upload Excel", "⌨️  Digitação Manual"])
    valores = []

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        up = st.file_uploader("Planilha Excel ou CSV", type=["xlsx","xls","csv"], key="dev_up")
        if up:
            try:
                col = st.text_input("Nome da coluna (vazio = primeira)", key="dev_col", placeholder="ex: cod_devolucao")
                vals = read_excel_column(up, column_name=col or None)
                st.success(f"✅ {len(vals)} valores lidos.")
                if st.button("▶  Executar Consulta", key="dev_ex"): valores = vals
            except Exception as e: st.error(str(e))

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        txt = st.text_area("Códigos de devolução", height=150,
            placeholder="DEV-001\nDEV-002\nDEV-003\n\nou: DEV-001, DEV-002", key="dev_txt")
        if st.button("▶  Executar Consulta", key="dev_mn"): valores = parse_text_input(txt)

    if valores:
        divider()
        with st.spinner("Consultando..."):
            try:
                df, meta = executar_pipeline("Devolução", valores)
                registrar(user["username"],"Devolução",meta["total_resultado"],meta["status"])
                show_result(df,"Devolução",meta)
            except Exception as e:
                st.error(f"Erro: {e}")
                registrar(user["username"],"Devolução",0,"error",str(e))
