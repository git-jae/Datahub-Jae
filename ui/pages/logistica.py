import streamlit as st
from ui.ui_helpers import page_header, divider, show_result, info_box, BD
from utils.excel_reader import read_excel_column
from utils.input_parser import parse_text_input
from pipeline.pipeline_executor import executar_pipeline
from logs.auditoria_execucao import registrar


def _excel_manual(key, placeholder, user, categoria):
    tab1, tab2 = st.tabs(["📁  Upload Excel", "⌨️  Digitação Manual"])
    valores = []
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        up = st.file_uploader("Planilha Excel ou CSV", type=["xlsx","xls","csv"], key=f"{key}_up")
        if up:
            try:
                col = st.text_input("Nome da coluna (vazio = primeira)", key=f"{key}_col")
                vals = read_excel_column(up, column_name=col or None)
                st.success(f"✅ {len(vals)} valores lidos.")
                if st.button("▶  Executar Consulta", key=f"{key}_ex"):
                    valores = vals
            except Exception as e:
                st.error(str(e))
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        txt = st.text_area("Valores", height=150, placeholder=placeholder, key=f"{key}_txt")
        if st.button("▶  Executar Consulta", key=f"{key}_mn"):
            valores = parse_text_input(txt)
    if valores:
        divider()
        with st.spinner("Consultando..."):
            try:
                df, meta = executar_pipeline(categoria, valores)
                registrar(user["username"], categoria, meta["total_resultado"], meta["status"])
                show_result(df, categoria, meta)
            except Exception as e:
                st.error(f"Erro: {e}")
                registrar(user["username"], categoria, 0, "error", str(e))


def render(user: dict):
    page_header("🚚", "Logística", "CONSULTAS")

    sub = st.selectbox(
        "Selecione a categoria",
        ["Rastreio de NF", "Telemarketing", "Devolução"],
        key="log_sub"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if sub == "Rastreio de NF":
        info_box(
            f"Informe os <strong style='color:#e8eaf2;'>números de Nota Fiscal</strong> (ex: NF-12345).<br>"
            f"Separe por <code style='background:{BD};padding:1px 6px;border-radius:4px;'>vírgula</code>, "
            f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>enter</code> ou "
            f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>espaço</code>.")
        _excel_manual("nf", "NF-12345\nNF-12346\n\nou: NF-12345, NF-12346", user, "Logística")

    elif sub == "Telemarketing":
        info_box(
            f"Informe os <strong style='color:#e8eaf2;'>números de telefone</strong> com DDD.<br>"
            f"Separe por <code style='background:{BD};padding:1px 6px;border-radius:4px;'>vírgula</code>, "
            f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>enter</code> ou "
            f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>espaço</code>.")
        st.markdown("<br>", unsafe_allow_html=True)
        txt = st.text_area("Números de telefone", height=150,
            placeholder="11987654321\n21998765432\n\nou: 11987654321, 21998765432", key="tele_txt")
        if st.button("▶  Executar Consulta", key="tele_mn"):
            valores = parse_text_input(txt)
            if not valores:
                st.warning("Informe ao menos um número.")
            else:
                divider()
                with st.spinner("Consultando..."):
                    try:
                        df, meta = executar_pipeline("Telemarketing", valores)
                        registrar(user["username"], "Telemarketing", meta["total_resultado"], meta["status"])
                        show_result(df, "Telemarketing", meta)
                    except Exception as e:
                        st.error(f"Erro: {e}")
                        registrar(user["username"], "Telemarketing", 0, "error", str(e))

    else:  # Devolução
        info_box(
            f"Informe os <strong style='color:#e8eaf2;'>códigos de devolução</strong> (ex: DEV-001).<br>"
            f"Separe por <code style='background:{BD};padding:1px 6px;border-radius:4px;'>vírgula</code>, "
            f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>enter</code> ou "
            f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>espaço</code>.")
        _excel_manual("dev", "DEV-001\nDEV-002\n\nou: DEV-001, DEV-002", user, "Devolução")
