import streamlit as st
from ui.ui_helpers import page_header, divider, show_result, info_box, BD
from utils.input_parser import parse_text_input
from pipeline.pipeline_executor import executar_pipeline
from logs.auditoria_execucao import registrar

def render(user: dict):
    page_header("📞", "Consulta Telemarketing", "CONTATOS")
    info_box(
        f"Informe os <strong style='color:#e8eaf2;'>números de telefone</strong> com DDD.<br>"
        f"Separe por <code style='background:{BD};padding:1px 6px;border-radius:4px;'>vírgula</code>, "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>enter</code> ou "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>espaço</code>.")

    st.markdown("<br>", unsafe_allow_html=True)
    txt = st.text_area("Números de telefone", height=160,
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
                    registrar(user["username"],"Telemarketing",meta["total_resultado"],meta["status"])
                    show_result(df,"Telemarketing",meta)
                except Exception as e:
                    st.error(f"Erro: {e}")
                    registrar(user["username"],"Telemarketing",0,"error",str(e))
