import streamlit as st
from ui.ui_helpers import page_header, divider, show_result, info_box, BD
from utils.excel_reader import read_excel_column
from utils.input_parser import parse_text_input
from pipeline.pipeline_executor import executar_pipeline
from logs.auditoria_execucao import registrar

def render(user: dict):
    page_header("🏢", "Consulta Comercial", "CLIENTES")
    info_box(
        f"Informe os <strong style='color:#e8eaf2;'>códigos de cliente</strong> via planilha ou digitação.<br>"
        f"Separe por <code style='background:{BD};padding:1px 6px;border-radius:4px;'>vírgula</code>, "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>enter</code> ou "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>espaço</code>.")

    tab1, tab2 = st.tabs(["📁  Upload Excel", "⌨️  Digitação Manual"])
    valores = []

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        up = st.file_uploader("Planilha Excel ou CSV", type=["xlsx","xls","csv"], key="com_up")
        if up:
            try:
                col = st.text_input("Nome da coluna (vazio = primeira)", key="com_col", placeholder="ex: codigo_cliente")
                vals = read_excel_column(up, column_name=col or None)
                st.success(f"✅ {len(vals)} valores lidos.")
                if st.button("▶  Executar Consulta", key="com_ex"): valores = vals
            except Exception as e: st.error(str(e))

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        txt = st.text_area("Códigos de cliente", height=150,
            placeholder="C001\nC002\nC003\n\nou: C001, C002, C003", key="com_txt")
        if st.button("▶  Executar Consulta", key="com_mn"): valores = parse_text_input(txt)

    if valores:
        divider()
        with st.spinner("Consultando..."):
            try:
                df, meta = executar_pipeline("Comercial", valores)
                registrar(user["username"],"Comercial",meta["total_resultado"],meta["status"])
                show_result(df,"Comercial",meta)
            except Exception as e:
                st.error(f"Erro: {e}")
                registrar(user["username"],"Comercial",0,"error",str(e))
