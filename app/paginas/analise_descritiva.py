import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

_AZUL     = "#1e3d59"
_VERMELHO = "#e53935"
_VERDE    = "#27ae60"
_TEMPLATE = "plotly_white"

_COL_MAP = {
    "Plantel":                "Tamanho do Plantel",
    "Estrangeiros":           "Nº de Estrangeiros",
    "Valor de Mercado Total": "VM Total (M€)",
    "Pontos":                 "Pontos",
}

_NUM_COLS = ["Plantel", "Estrangeiros", "Valor de Mercado Total", "Pontos"]


@st.cache_data(show_spinner=False)
def _load():
    df = pd.read_excel(os.path.join("dados", "BASE_FINAL.xlsx"), sheet_name="CLUBES")
    df.columns = df.columns.str.strip()
    return df


def main():
    st.markdown('<p class="section-title">Análise Descritiva — Brasileirão Série A</p>',
                unsafe_allow_html=True)

    df = _load()
    existentes = [c for c in _NUM_COLS if c in df.columns]
    temporadas = sorted([t for t in df["Temporada"].unique() if t != 2025])

    # ── Seletor de temporada ──────────────────────────────────────────────────
    col_sel, _ = st.columns([1, 3])
    with col_sel:
        sel_ano = st.selectbox("Temporada para análise:", temporadas, index=len(temporadas) - 1)

    df_ano = df[df["Temporada"] == sel_ano]

    # ── KPIs da temporada ─────────────────────────────────────────────────────
    st.markdown(f'<p class="section-title">Temporada {sel_ano} — Visão Geral</p>',
                unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Clubes", df_ano["Clube"].nunique())

    if "Plantel" in df_ano.columns:
        k2.metric("Plantel médio", f"{df_ano['Plantel'].mean():.1f} atletas")
    if "Valor de Mercado Total" in df_ano.columns:
        k3.metric("VM médio (M€)", f"{df_ano['Valor de Mercado Total'].mean():.1f}")
    if "Pontos" in df_ano.columns:
        k4.metric("Pontos médios", f"{df_ano['Pontos'].mean():.1f}")

    tab_est, tab_clube, tab_hist = st.tabs([
        "📋  Estatísticas Descritivas",
        "🔍  Análise por Clube",
        "📈  Histórico Comparativo",
    ])

    # ── TAB 1: Estatísticas ───────────────────────────────────────────────────
    with tab_est:
        desc = df_ano[existentes].describe().T
        desc.index = [_COL_MAP.get(i, i) for i in desc.index]
        desc = desc.rename(columns={
            "count": "N", "mean": "Média", "std": "Desvio Padrão",
            "min": "Mínimo", "25%": "Q1", "50%": "Mediana", "75%": "Q3", "max": "Máximo",
        })
        st.dataframe(desc.round(2), use_container_width=True)

        # Boxplots lado a lado
        df_melt = (df_ano[["Clube"] + existentes]
                   .melt(id_vars="Clube", var_name="Indicador", value_name="Valor"))
        df_melt["Indicador"] = df_melt["Indicador"].map(lambda x: _COL_MAP.get(x, x))

        fig_box = px.box(
            df_melt, x="Indicador", y="Valor", color="Indicador",
            points="all", template=_TEMPLATE,
            title=f"Distribuição das variáveis — {sel_ano}",
        )
        fig_box.update_layout(height=400, showlegend=False, margin=dict(b=40))
        st.plotly_chart(fig_box, use_container_width=True)

        # Tabela completa por clube
        st.markdown(f"**Dados por clube — {sel_ano}**")
        tabela = df_ano[["Clube"] + existentes].rename(columns=_COL_MAP).reset_index(drop=True)
        st.dataframe(tabela, use_container_width=True, hide_index=True)

    # ── TAB 2: Por Clube ──────────────────────────────────────────────────────
    with tab_clube:
        clubes = sorted(df["Clube"].unique())
        default_idx = clubes.index("Flamengo") if "Flamengo" in clubes else 0
        sel_clube = st.selectbox("Clube:", clubes, index=default_idx, key="sel_clube")

        df_ca = df_ano[df_ano["Clube"] == sel_clube]

        if df_ca.empty:
            st.info(f"{sel_clube} não disputou a Série A em {sel_ano}.")
        else:
            # KPIs do clube
            ck1, ck2, ck3, ck4 = st.columns(4)
            if "Plantel" in df_ca.columns:
                ck1.metric("Plantel", int(df_ca["Plantel"].iloc[0]))
            if "Estrangeiros" in df_ca.columns:
                ck2.metric("Estrangeiros", int(df_ca["Estrangeiros"].iloc[0]))
            if "Valor de Mercado Total" in df_ca.columns:
                ck3.metric("VM Total (M€)", f"{df_ca['Valor de Mercado Total'].iloc[0]:.1f}")
            if "Pontos" in df_ca.columns:
                ck4.metric("Pontos", int(df_ca["Pontos"].iloc[0]))

            # Bar de indicadores do clube vs média da temporada
            medias = df_ano[existentes].mean()
            clube_vals = df_ca[existentes].iloc[0]

            comp_df = pd.DataFrame({
                "Indicador": [_COL_MAP.get(c, c) for c in existentes],
                sel_clube:   clube_vals.values,
                "Média Série A": medias.values,
            }).melt(id_vars="Indicador", var_name="Tipo", value_name="Valor")

            fig_comp = px.bar(
                comp_df, x="Indicador", y="Valor", color="Tipo", barmode="group",
                color_discrete_map={sel_clube: _AZUL, "Média Série A": "#94a3b8"},
                template=_TEMPLATE,
                title=f"{sel_clube} vs Média da Série A — {sel_ano}",
                text_auto=".1f",
            )
            fig_comp.update_layout(height=380, margin=dict(b=40))
            fig_comp.update_traces(textposition="outside")
            st.plotly_chart(fig_comp, use_container_width=True)

    # ── TAB 3: Histórico ──────────────────────────────────────────────────────
    with tab_hist:
        clubes_hist = sorted(df["Clube"].unique())
        default_h = [c for c in ["Flamengo", "Palmeiras", "Corinthians"] if c in clubes_hist]
        sel_multi = st.multiselect("Clubes para comparar:", clubes_hist,
                                   default=default_h, key="multi_hist")

        if not sel_multi:
            st.warning("Selecione ao menos um clube.")
        else:
            ind_hist = st.selectbox(
                "Indicador:",
                [_COL_MAP.get(c, c) for c in existentes],
                key="ind_hist",
            )
            # Reverter mapeamento
            inv_map = {v: k for k, v in _COL_MAP.items()}
            col_orig = inv_map.get(ind_hist, ind_hist)

            df_hist = (df[(df["Clube"].isin(sel_multi)) & (df["Temporada"] != 2025)]
                       .sort_values("Temporada"))

            fig_line = px.line(
                df_hist, x="Temporada", y=col_orig, color="Clube",
                markers=True, template=_TEMPLATE,
                labels={col_orig: ind_hist},
                title=f"Evolução de {ind_hist} por Temporada",
                text=col_orig,
            )
            fig_line.update_traces(textposition="top center", texttemplate="%{text:.0f}")
            fig_line.update_layout(height=440, margin=dict(b=40))
            st.plotly_chart(fig_line, use_container_width=True)

            # Correlação VM × Pontos (se disponíveis)
            if "Valor de Mercado Total" in df.columns and "Pontos" in df.columns:
                df_corr = df[(df["Clube"].isin(sel_multi)) & (df["Temporada"] != 2025)]
                fig_sc = px.scatter(
                    df_corr, x="Valor de Mercado Total", y="Pontos",
                    color="Clube", size="Plantel" if "Plantel" in df_corr.columns else None,
                    hover_data=["Temporada"],
                    template=_TEMPLATE,
                    labels={"Valor de Mercado Total": "VM Total (M€)"},
                    title="Correlação: Valor de Mercado × Pontos",

                )
                fig_sc.update_layout(height=400, margin=dict(b=40))
                st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown(
        '<div class="custom-footer">TCC · Leonardo Feitosa · Ciência de Dados – UFPB · 2025</div>',
        unsafe_allow_html=True,
    )
