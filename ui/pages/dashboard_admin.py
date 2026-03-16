import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from logs.log_reader import get_logs_df, get_summary_stats
from ui.ui_helpers import page_header, divider, _kpi_card, A, BG, BD, T1, T2, T3

_C   = {"Comercial":A,"Telemarketing":"#a78bfa","Devolução":"#f0883e","Logística":"#3dd68c"}
_LAY = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Nunito, sans-serif", color=T2, size=11),
            margin=dict(l=10,r=10,t=28,b=10))

def _sec(title):
    st.markdown(f'<div style="font-family:Nunito,sans-serif;font-size:13px;font-weight:800;'
                f'color:{T2};text-transform:uppercase;letter-spacing:0.8px;margin-bottom:10px;">'
                f'{title}</div>', unsafe_allow_html=True)

def render(user: dict):
    page_header("📊", "Dashboard", "ANALYTICS")
    df = get_logs_df(limit=1000)

    if df.empty:
        st.info("Nenhuma consulta registrada ainda.")
        return

    stats = get_summary_stats(df)

    c1,c2,c3,c4 = st.columns(4)
    for col,label,val,color in [
        (c1,"Total de Consultas",   stats["total"],                  T1),
        (c2,"Registros Retornados", stats.get("registros_total",0),  A),
        (c3,"Categorias Ativas",    len(stats["por_categoria"]),     "#a78bfa"),
        (c4,"Usuários Ativos",      len(stats["por_usuario"]),       T1),
    ]:
        with col: st.markdown(_kpi_card(label,f"{val:,}",color), unsafe_allow_html=True)

    divider()

    ca, cb = st.columns([3,2])
    with ca:
        _sec("Consultas por Categoria")
        cat_df = pd.DataFrame(list(stats["por_categoria"].items()), columns=["Categoria","N"])
        fig = go.Figure(go.Bar(
            x=cat_df["Categoria"], y=cat_df["N"],
            marker_color=[_C.get(c,A) for c in cat_df["Categoria"]],
            text=cat_df["N"], textposition="outside",
            textfont=dict(size=13,color=T1,family="Nunito")))
        fig.update_layout(**_LAY, height=260,
            xaxis=dict(showgrid=False,tickfont=dict(size=13,color=T1)),
            yaxis=dict(showgrid=True,gridcolor=BD,zeroline=False,showticklabels=False))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with cb:
        _sec("Por Usuário")
        ud  = pd.DataFrame(list(stats["por_usuario"].items()), columns=["Usuário","N"])
        fig2 = px.pie(ud, names="Usuário", values="N", hole=0.58,
            color_discrete_sequence=[A,"#a78bfa","#f0883e","#3dd68c","#f47067"])
        fig2.update_traces(textposition="outside", textinfo="label+percent",
            textfont=dict(size=10,family="Nunito",color=T1))
        fig2.update_layout(**_LAY, height=260, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    _sec("Consultas por Hora")
    dfc       = df.copy()
    dfc["hora"] = dfc["timestamp"].dt.floor("h")
    tl        = dfc.groupby(["hora","categoria"]).size().reset_index(name="n")
    if not tl.empty:
        fig3 = px.area(tl, x="hora", y="n", color="categoria",
            color_discrete_map=_C, labels={"hora":"","n":"Consultas","categoria":""})
        fig3.update_traces(mode="lines+markers", line_width=2)
        fig3.update_layout(**_LAY, height=200,
            xaxis=dict(showgrid=False,tickfont=dict(size=10)),
            yaxis=dict(showgrid=True,gridcolor=BD,tickfont=dict(size=10)),
            legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=10)))
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

    divider()
    _sec("Últimas Execuções")
    rec = df.head(15)[["timestamp","usuario","categoria","quantidade","status"]].copy()
    rec["timestamp"] = rec["timestamp"].dt.strftime("%d/%m/%Y %H:%M")
    rec.columns = ["Data/Hora","Usuário","Categoria","Registros","Status"]
    st.dataframe(rec, use_container_width=True, hide_index=True)
