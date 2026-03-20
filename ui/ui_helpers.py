import io
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

A  = "#00C4B4"   # accent teal Jaé
AD = "#00A8A0"   # accent dark
BG = "#1a1e2a"   # card background
BD = "#2a2f3d"   # border
T1 = "#e8eaf2"   # text primary
T2 = "#8b90a8"   # text secondary
T3 = "#555c72"   # text muted


def load_css():
    p = Path(__file__).parent.parent / "styles" / "style.css"
    if p.exists():
        st.markdown(f"<style>{p.read_text()}</style>", unsafe_allow_html=True)

    st.markdown("""
        <script>
        (function() {
            localStorage.removeItem('stSidebarCollapsed-');
            Object.keys(localStorage)
                .filter(k => k.startsWith('stSidebarCollapsed'))
                .forEach(k => localStorage.removeItem(k));
        })();
        </script>
    """, unsafe_allow_html=True)


def sidebar_logo():
    st.sidebar.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;
                    padding:0 0 20px 0;border-bottom:1px solid {BD};margin-bottom:18px;">
            <div style="background:{A};font-family:'Nunito',sans-serif;font-weight:900;
                        font-size:19px;color:#fff;width:44px;height:44px;border-radius:12px;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;
                        box-shadow:0 4px 16px rgba(0,196,180,0.35);">Jaé</div>
            <div>
                <div style="font-family:'Nunito',sans-serif;font-weight:800;font-size:16px;
                            color:{T1};line-height:1.2;">Datahub</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.3);margin-top:2px;">
                    Internal Data Platform</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def sidebar_user_badge(user: dict):
    role = "Administrador" if user.get("role") == "admin" else "Operador"
    name = user.get("display_name", user.get("username"))
    st.sidebar.markdown(f"""
        <div style="background:rgba(0,196,180,0.08);border:1px solid rgba(0,196,180,0.2);
                    border-radius:8px;padding:10px 14px;margin-bottom:18px;">
            <div style="font-family:'Nunito',sans-serif;font-weight:700;
                        font-size:13px;color:{T1};">👤 {name}</div>
            <div style="font-size:11px;font-weight:600;color:{A};margin-top:2px;">{role}</div>
        </div>
    """, unsafe_allow_html=True)


def page_header(icon: str, title: str, tag: str = ""):
    tag_html = (f'<span style="font-size:11px;font-weight:700;letter-spacing:0.8px;'
                f'text-transform:uppercase;color:{A};background:rgba(0,196,180,0.1);'
                f'border:1px solid rgba(0,196,180,0.25);padding:3px 10px;border-radius:20px;">'
                f'{tag}</span>') if tag else ""
    st.markdown(f"""
        <div style="background:{BG};border-radius:12px;padding:18px 22px;margin-bottom:22px;
                    display:flex;align-items:center;gap:14px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.3);border-left:4px solid {A};">
            <span style="font-size:26px;">{icon}</span>
            <h1 style="font-family:'Nunito',sans-serif;font-size:21px;font-weight:800;
                       color:{T1};margin:0;">{title}</h1>
            {tag_html}
        </div>
    """, unsafe_allow_html=True)


def divider():
    st.markdown(f'<hr style="border:none;border-top:1px solid {BD};margin:22px 0;">',
                unsafe_allow_html=True)


def info_box(text: str, title: str = "ℹ️ Como usar"):
    st.markdown(f"""
        <div style="background:{BG};border:1px solid {BD};border-radius:12px;
                    padding:16px 20px;margin-bottom:16px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.3);font-size:14px;color:{T2};">
            <div style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:800;
                        color:{A};text-transform:uppercase;letter-spacing:0.8px;
                        margin-bottom:8px;">{title}</div>
            {text}
        </div>
    """, unsafe_allow_html=True)


def _kpi_card(label: str, value, color: str = T1) -> str:
    return f"""
        <div style="background:{BG};border:1px solid {BD};border-radius:12px;
                    padding:18px 20px;box-shadow:0 2px 8px rgba(0,0,0,0.3);">
            <div style="font-size:11px;font-weight:700;color:{T3};text-transform:uppercase;
                        letter-spacing:0.8px;margin-bottom:8px;">{label}</div>
            <div style="font-family:'Nunito',sans-serif;font-size:32px;font-weight:800;
                        color:{color};line-height:1;">{value}</div>
        </div>"""


def show_result(df: pd.DataFrame, categoria: str, meta: dict):
    if df.empty:
        st.warning("Nenhum resultado encontrado.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(_kpi_card("Consultados", meta.get("total_limpo", 0)), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi_card("Encontrados", meta.get("total_resultado", 0), A), unsafe_allow_html=True)
    with c3:
        taxa = 0
        if meta.get("total_limpo", 0) > 0:
            taxa = round(meta["total_resultado"] / meta["total_limpo"] * 100)
        st.markdown(_kpi_card("Taxa de Localização", f"{taxa}%"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:Nunito,sans-serif;font-size:13px;font-weight:800;'
                f'color:{T2};text-transform:uppercase;letter-spacing:0.8px;margin-bottom:10px;">'
                f'Resultado — {categoria}</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = (categoria.lower()
            .replace("ã","a").replace("ç","c").replace("é","e").replace(" ","_"))
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Resultado")
    st.download_button("⬇ Baixar Excel", data=buf.getvalue(),
        file_name=f"resultado_{slug}_{ts}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")