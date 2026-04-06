import streamlit as st
import pandas as pd
import plotly.express as px

from app.utils.processamento import carregar_dados_excel as carregar_dados

_AZUL     = "#1e3d59"
_VERMELHO = "#e53935"
_VERDE    = "#27ae60"
_TEMPLATE = "plotly_white"

_STATUS_MAP = {
    "Rebaixado":            "Rebaixado",
    "Top4":                 "Top 4",
    "Top 4":                "Top 4",
    "SerieA":               "Série A",
    "SérieA":               "Série A",
    "Série A":              "Série A",
    "SerieB_Para_SerieA":   "Promovido",
    "Serie B para Série A": "Promovido",
}

_COR_STATUS = {
    "Rebaixado":  _VERMELHO,
    "Top 4":      _AZUL,
    "Série A":    _VERDE,
    "Promovido":  "#f57c00",
}


def _preparar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Temporada"] = df["Temporada"].astype(str).str.replace(",", "").str.strip()
    df = df[df["Temporada"] != ""]

    if "Valor de Mercado Total" in df.columns:
        df.rename(columns={"Valor de Mercado Total": "VM Total (M€)"}, inplace=True)

    if "Situacao" in df.columns:
        df["Situação"] = df["Situacao"].map(lambda x: _STATUS_MAP.get(str(x).strip(), str(x).strip()))
    else:
        df["Situação"] = "—"

    return df


def main():
    st.markdown('<p class="section-title">Base de Dados Histórica — Brasileirão Série A</p>',
                unsafe_allow_html=True)

    df_raw = carregar_dados()
    df = _preparar(df_raw)

    # ── Filtros ───────────────────────────────────────────────────────────────
    with st.expander("🔍 Filtros", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 1])
        with fc1:
            sit_opts = sorted(df["Situação"].dropna().unique())
            sit_sel  = st.multiselect("Situação", sit_opts, default=sit_opts, key="sit")
        with fc2:
            clube_opts = sorted(df["Clube"].dropna().unique())
            clube_sel  = st.multiselect("Clube", clube_opts, default=[], key="clube",
                                        placeholder="Todos")
        with fc3:
            temp_opts = sorted(df["Temporada"].dropna().unique())
            temp_sel  = st.multiselect("Temporada", temp_opts, default=[], key="temp",
                                       placeholder="Todas")
        with fc4:
            min_vm = st.number_input("VM mínimo (M€)", value=0.0, step=5.0)

    sit_filtrada   = sit_sel or sit_opts
    clube_filtrado = clube_sel or clube_opts
    temp_filtrada  = temp_sel or temp_opts

    vm_col = "VM Total (M€)" if "VM Total (M€)" in df.columns else None
    mask = (
        df["Situação"].isin(sit_filtrada) &
        df["Clube"].isin(clube_filtrado) &
        df["Temporada"].isin(temp_filtrada)
    )
    if vm_col:
        mask &= df[vm_col] >= min_vm
    df_f = df[mask]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Registros", len(df_f))
    k2.metric("Clubes únicos", df_f["Clube"].nunique())
    k3.metric("Temporadas", df_f["Temporada"].nunique())
    reb_n = (df_f["Situação"] == "Rebaixado").sum()
    k4.metric("Rebaixamentos", reb_n)

    # Tabela
    st.dataframe(df_f.reset_index(drop=True), use_container_width=True, height=340)
    csv = df_f.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Exportar CSV", csv, "dados_filtrados.csv", "text/csv")

    st.markdown("---")

    tab_comp, tab_dist, tab_evol = st.tabs([
        "📊  Comparação entre Clubes",
        "🥧  Distribuição por Situação",
        "📈  Evolução Temporal",
    ])

    # ── TAB 1: Comparação ────────────────────────────────────────────────────
    with tab_comp:
        if df_f.empty:
            st.info("Sem dados para exibir. Ajuste os filtros.")
        else:
            metric_col = st.selectbox(
                "Indicador a comparar",
                [c for c in ["Pontos", "VM Total (M€)", "Plantel", "Estrangeiros"] if c in df_f.columns],
            )
            df_bar = (df_f.groupby("Clube")[metric_col].mean()
                         .sort_values(ascending=False)
                         .reset_index()
                         .rename(columns={metric_col: f"{metric_col} (média)"}))

            fig = px.bar(
                df_bar.head(20),
                x="Clube", y=f"{metric_col} (média)",
                color=f"{metric_col} (média)",
                color_continuous_scale=["#cfe2ff", _AZUL],
                text_auto=".1f",
                template=_TEMPLATE,
                title=f"Top 20 clubes — {metric_col} (média das temporadas filtradas)",
            )
            fig.update_layout(
                xaxis_tickangle=-35, height=420,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=50, b=80),
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2: Distribuição ──────────────────────────────────────────────────
    with tab_dist:
        if df_f.empty:
            st.info("Sem dados.")
        else:
            c_pie, c_bar = st.columns(2)
            with c_pie:
                fig_pie = px.pie(
                    df_f, names="Situação",
                    color="Situação",
                    color_discrete_map=_COR_STATUS,
                    hole=0.5,
                    template=_TEMPLATE,
                    title="Proporção por Situação",
                )
                fig_pie.update_traces(textinfo="percent+label")
                fig_pie.update_layout(height=380, showlegend=False)
                st.plotly_chart(fig_pie, use_container_width=True)

            with c_bar:
                df_sit_temp = (df_f.groupby(["Temporada", "Situação"])
                                   .size()
                                   .reset_index(name="Contagem"))
                fig_bar2 = px.bar(
                    df_sit_temp, x="Temporada", y="Contagem", color="Situação",
                    color_discrete_map=_COR_STATUS,
                    template=_TEMPLATE,
                    title="Contagem por Temporada e Situação",
                    barmode="stack",
                )
                fig_bar2.update_layout(height=380, margin=dict(b=60))
                fig_bar2.update_xaxes(tickangle=-45)
                st.plotly_chart(fig_bar2, use_container_width=True)

    # ── TAB 3: Evolução Temporal ─────────────────────────────────────────────
    with tab_evol:
        if df_f.empty or df_f["Clube"].nunique() == 0:
            st.info("Selecione ao menos um clube nos filtros para ver a evolução.")
        else:
            evol_col = st.selectbox(
                "Indicador para evolução",
                [c for c in ["Pontos", "VM Total (M€)", "Plantel", "Estrangeiros"] if c in df_f.columns],
                key="evol_col",
            )
            df_evol = (df_f.groupby(["Clube", "Temporada"])[evol_col]
                           .mean()
                           .reset_index()
                           .sort_values("Temporada"))

            fig_line = px.line(
                df_evol, x="Temporada", y=evol_col, color="Clube",
                markers=True, template=_TEMPLATE,
                title=f"Evolução de {evol_col} por Temporada",
                labels={evol_col: evol_col, "Temporada": "Temporada"},
            )
            fig_line.update_layout(height=430, margin=dict(b=40))
            st.plotly_chart(fig_line, use_container_width=True)

    st.markdown(
        '<div class="custom-footer">TCC · Leonardo Feitosa · Ciência de Dados – UFPB · 2025</div>',
        unsafe_allow_html=True,
    )
