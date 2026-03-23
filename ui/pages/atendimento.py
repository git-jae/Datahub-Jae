import streamlit as st
from ui.ui_helpers import page_header, divider, info_box, BD, A, BG, T2
from utils.input_parser import parse_text_input
from logs.auditoria_execucao import registrar
from services.consulta_atendimento import executar_pipeline


def render(user: dict):
    page_header("🎧", "Consulta Atendimento")

    info_box(
        "Informe o <strong style='color:#e8eaf2;'>número lógico (ou físico) do cartão</strong> "
        "para verificar se é um cartão inconsistente.<br>"
        f"A consulta analisa as transações dos <strong style='color:#e8eaf2;'>últimos 30 dias</strong>. "
        f"Separe por <code style='background:{BD};padding:1px 6px;border-radius:4px;'>vírgula</code>, "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>enter</code> ou "
        f"<code style='background:{BD};padding:1px 6px;border-radius:4px;'>espaço</code>."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📁  Upload Excel", "⌨️  Digitação Manual"])

    # ── Upload Excel ──────────────────────────────────────────────────────────
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        up = st.file_uploader(
            "Planilha Excel",
            type=["xlsx", "xls"],
            key="atd_up",
        )
        if up:
            try:
                import pandas as pd
                df_in = pd.read_excel(up)
                valores = df_in.iloc[:, 0].dropna().astype(str).str.strip().unique().tolist()
                st.success(f"✅ {len(valores)} número(s) lido(s).")
                if st.button("▶  Executar Consulta", key="atd_ex"):
                    _run(valores, user)
            except Exception as e:
                st.error(f"Erro ao ler planilha: {e}")

    # ── Digitação Manual ──────────────────────────────────────────────────────
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        txt = st.text_area(
            "Números lógicos",
            height=150,
            placeholder="3089050011111111 ou: 056826XX000",
            key="atd_txt",
        )
        if st.button("▶  Executar Consulta", key="atd_mn"):
            _run(parse_text_input(txt), user)


def _run(valores: list, user: dict):
    """Executa a consulta para cada número e exibe os resultados."""
    if not valores:
        st.warning("Informe ao menos um número lógico.")
        return

    divider()

    resultados = []
    erros = 0

    with st.spinner(f"Consultando {len(valores)} número(s)..."):
        for num in valores:
            try:
                df = executar_pipeline("atendimento", [num])
                if not df.empty:
                    resultados.append(df)
            except Exception as e:
                erros += 1
                registrar(user["username"], "Atendimento", 0, "error", str(e))

    if not resultados:
        st.warning("Nenhum resultado encontrado.")
        return

    import pandas as pd
    df_final = pd.concat(resultados, ignore_index=True)

    total      = len(df_final)
    cartao_tr  = (df_final["Resultado"] == "Cartão Com Inconsistência").sum()
    nao_cartao = (df_final["Resultado"] == "Cartão Sem Inconsistência").sum()
    sem_trans  = total - cartao_tr - nao_cartao

    # ── KPIs ─────────────────────────────────────────────────────────────────
    from ui.ui_helpers import _kpi_card, T1
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(_kpi_card("Consultados",     total),           unsafe_allow_html=True)
    with c2: st.markdown(_kpi_card("Cartão Inconsistente",    cartao_tr,  A),   unsafe_allow_html=True)
    with c3: st.markdown(_kpi_card("Cartão OK",       nao_cartao, "#a78bfa"), unsafe_allow_html=True)
    with c4: st.markdown(_kpi_card("Sem Transações",  sem_trans,  "#f0883e"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-family:Nunito,sans-serif;font-size:13px;font-weight:800;'
        f'color:{T2};text-transform:uppercase;letter-spacing:0.8px;margin-bottom:10px;">'
        f'Resultado — Atendimento CCO</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(df_final, use_container_width=True, hide_index=True)

    # ── Download ──────────────────────────────────────────────────────────────
    import io
    from datetime import datetime
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df_final.to_excel(w, index=False, sheet_name="Atendimento")
    st.download_button(
        "⬇ Baixar Excel",
        data=buf.getvalue(),
        file_name=f"resultado_atendimento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # ── Auditoria ─────────────────────────────────────────────────────────────
    registrar(user["username"], "Atendimento", total, "success")