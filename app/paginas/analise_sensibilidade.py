import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from app.utils.processamento import fazer_previsao

_AZUL     = "#1e3d59"
_VERMELHO = "#e53935"
_VERDE    = "#27ae60"
_TEMPLATE = "plotly_white"

# Valores-base (médias históricas da Série A)
_BASE = {"Plantel": 28, "Estrangeiros": 4, "Valor de Mercado Total": 85.0}


@st.cache_data(show_spinner=False)
def _calc_sensibilidade():
    """Pré-computa curvas de sensibilidade para os 3 fatores."""
    plantel_vals  = list(range(15, 51, 1))
    estrang_vals  = list(range(0, 16, 1))
    valor_vals    = list(range(5, 301, 5))

    def _prob(p, e, v):
        d = pd.DataFrame({"Plantel": [p], "Estrangeiros": [e], "Valor de Mercado Total": [v]})
        _, pr = fazer_previsao(d)
        return pr[0][0]  # prob de Rebaixamento (classe 0)

    df_p = pd.DataFrame({
        "Tamanho do Elenco": plantel_vals,
        "Prob. Rebaixamento": [_prob(p, _BASE["Estrangeiros"], _BASE["Valor de Mercado Total"])
                               for p in plantel_vals],
    })
    df_e = pd.DataFrame({
        "Nº de Estrangeiros": estrang_vals,
        "Prob. Rebaixamento": [_prob(_BASE["Plantel"], e, _BASE["Valor de Mercado Total"])
                               for e in estrang_vals],
    })
    df_v = pd.DataFrame({
        "Valor de Mercado (M€)": valor_vals,
        "Prob. Rebaixamento": [_prob(_BASE["Plantel"], _BASE["Estrangeiros"], v)
                               for v in valor_vals],
    })
    return df_p, df_e, df_v


@st.cache_data(show_spinner=False)
def _calc_interacao():
    """Pré-computa grade para heatmap Plantel × Valor de Mercado."""
    plantel_vals = list(range(15, 51, 5))
    valor_vals   = list(range(5, 301, 30))
    rows = []
    for p in plantel_vals:
        for v in valor_vals:
            d = pd.DataFrame({"Plantel": [p], "Estrangeiros": [_BASE["Estrangeiros"]],
                              "Valor de Mercado Total": [v]})
            _, pr = fazer_previsao(d)
            rows.append({"Plantel": p, "Valor de Mercado (M€)": v,
                         "Prob. Rebaixamento": round(pr[0][0] * 100, 1)})
    return pd.DataFrame(rows)


def _hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _linha(df, x, cor, titulo, linha_base=None):
    fig = px.area(df, x=x, y="Prob. Rebaixamento",
                  template=_TEMPLATE, color_discrete_sequence=[cor])
    fig.update_traces(
        line_width=2.5,
        fillcolor=_hex_to_rgba(cor),
        hovertemplate=f"<b>{x}:</b> %{{x}}<br><b>Prob. Rebaixamento:</b> %{{y:.1%}}<extra></extra>",
    )
    if linha_base is not None:
        fig.add_vline(x=linha_base, line_dash="dot", line_color="gray", opacity=0.6,
                      annotation_text="Base", annotation_position="top right")
    fig.add_hline(y=0.5, line_dash="dash", line_color=_VERMELHO, opacity=0.4,
                  annotation_text="50 %", annotation_position="right")
    fig.update_layout(
        title=dict(text=titulo, font_size=13, x=0),
        yaxis=dict(title="Prob. Rebaixamento", tickformat=".0%", range=[0, 1]),
        xaxis_title=x,
        height=320,
        margin=dict(l=10, r=10, t=45, b=40),
    )
    return fig


def main():
    st.markdown('<p class="section-title">Análise de Sensibilidade</p>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        Mostra como cada variável independente influencia a probabilidade de rebaixamento,
        mantendo as demais fixadas nos <b>valores médios históricos da Série A</b>
        (Plantel&nbsp;=&nbsp;28 · Estrangeiros&nbsp;=&nbsp;4 · Valor de Mercado&nbsp;=&nbsp;85&nbsp;M€).
    </div>
    """, unsafe_allow_html=True)

    # KPIs dos valores-base
    c1, c2, c3 = st.columns(3)
    c1.metric("Plantel base", f"{_BASE['Plantel']} atletas")
    c2.metric("Estrangeiros base", f"{_BASE['Estrangeiros']}")
    c3.metric("Valor de Mercado base", f"{_BASE['Valor de Mercado Total']:.0f} M€")

    tab_uni, tab_int = st.tabs(["📈  Análise Univariada", "🗺️  Interação entre Variáveis"])

    with tab_uni:
        with st.spinner("Calculando curvas de sensibilidade..."):
            df_p, df_e, df_v = _calc_sensibilidade()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.plotly_chart(
                _linha(df_p, "Tamanho do Elenco", _AZUL,
                       "Impacto do Tamanho do Elenco", _BASE["Plantel"]),
                use_container_width=True,
            )
        with col2:
            st.plotly_chart(
                _linha(df_e, "Nº de Estrangeiros", "#7c3aed",
                       "Impacto do Nº de Estrangeiros", _BASE["Estrangeiros"]),
                use_container_width=True,
            )
        with col3:
            st.plotly_chart(
                _linha(df_v, "Valor de Mercado (M€)", _VERMELHO,
                       "Impacto do Valor de Mercado", _BASE["Valor de Mercado Total"]),
                use_container_width=True,
            )

        st.markdown("""
        <div class="info-box">
            <b>Interpretação:</b> curvas descendentes indicam que aumentar a variável
            <em>reduz</em> o risco de rebaixamento. A linha tracejada vermelha marca o limiar de 50 %.
        </div>
        """, unsafe_allow_html=True)

    with tab_int:
        st.markdown('<p class="section-title">Interação: Plantel × Valor de Mercado</p>',
                    unsafe_allow_html=True)
        st.caption(
            f"Estrangeiros fixados em {_BASE['Estrangeiros']}. "
            "Tons mais escuros = maior risco de rebaixamento."
        )

        with st.spinner("Calculando grade de interação..."):
            df_int = _calc_interacao()

        df_pivot = df_int.pivot(
            index="Plantel", columns="Valor de Mercado (M€)", values="Prob. Rebaixamento"
        )

        fig_heat = px.imshow(
            df_pivot,
            color_continuous_scale=["#27ae60", "#f39c12", "#e53935"],
            aspect="auto",
            labels=dict(x="Valor de Mercado (M€)", y="Plantel", color="Prob. Reb. (%)"),
            template=_TEMPLATE,
        )
        fig_heat.update_layout(
            title=dict(text="Prob. de Rebaixamento (%) — Plantel × Valor de Mercado", font_size=13),
            height=400,
            margin=dict(l=10, r=10, t=50, b=40),
            coloraxis_colorbar=dict(title="Prob. (%)", ticksuffix=" %"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # Scatter 3D
        fig_3d = px.scatter_3d(
            df_int,
            x="Plantel",
            y="Valor de Mercado (M€)",
            z="Prob. Rebaixamento",
            color="Prob. Rebaixamento",
            color_continuous_scale=["#27ae60", "#f39c12", "#e53935"],
            opacity=0.85,
            labels={"Prob. Rebaixamento": "Prob. (%)"},
            template=_TEMPLATE,
        )
        fig_3d.update_layout(
            height=540,
            margin=dict(l=0, r=0, t=30, b=0),
            scene=dict(zaxis_title="Prob. Reb. (%)"),
        )
        st.plotly_chart(fig_3d, use_container_width=True)

    st.markdown(
        '<div class="custom-footer">TCC · Leonardo Feitosa · Ciência de Dados – UFPB · 2025</div>',
        unsafe_allow_html=True,
    )
