import streamlit as st
import pandas as pd
import plotly.express as px

from app.utils.processamento import carregar_dados_excel as carregar_dados, carregar_desempenho_com_janelas

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


_RENOMEAR_JANELAS = {
    "Pts_media_3":          "Pts Média 3T",
    "Pts_media_5":          "Pts Média 5T",
    "SG_media_3":           "SG Média 3T",
    "SG_media_5":           "SG Média 5T",
    "Gols_Pro_media_3":     "Gols+ Média 3T",
    "Gols_Pro_media_5":     "Gols+ Média 5T",
    "Gols_Contra_media_3":  "Gols- Média 3T",
    "Gols_Contra_media_5":  "Gols- Média 5T",
    "V_media_3":            "Vitórias Média 3T",
    "V_media_5":            "Vitórias Média 5T",
    "Aproveitamento_media_3": "Aprov. Média 3T",
    "Aproveitamento_media_5": "Aprov. Média 5T",
}

_COLUNAS_BASE = ["Clube", "Temporada", "Plantel", "Estrangeiros", "VM Total (M€)", "Situação"]


def _preparar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Temporada"] = df["Temporada"].astype(str).str.replace(",", "").str.strip()
    df = df[df["Temporada"] != ""]

    if "Valor de Mercado Total" in df.columns:
        df.rename(columns={"Valor de Mercado Total": "VM Total (M€)"}, inplace=True)

    if "Situacao" in df.columns:
        df["Situação"] = df["Situacao"].map(
            lambda x: _STATUS_MAP.get(str(x).strip(), str(x).strip())
        )
        df = df[df["Situação"] != "nan"]
    else:
        df["Situação"] = "—"

    df.rename(columns=_RENOMEAR_JANELAS, inplace=True)

    jan_cols = [v for v in _RENOMEAR_JANELAS.values() if v in df.columns]
    cols = [c for c in _COLUNAS_BASE if c in df.columns] + jan_cols
    return df[cols]


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

    tab_comp, tab_dist, tab_evol, tab_jan = st.tabs([
        "📊  Comparação entre Clubes",
        "🥧  Distribuição por Situação",
        "📈  Evolução Temporal",
        "🔁  Janelas Deslizantes",
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

    # ── TAB 4: Janelas Deslizantes ───────────────────────────────────────────
    with tab_jan:
        st.markdown("""
        <div style="background:#1e3d59;color:#ffffff;border-left:4px solid #f57c00;padding:12px 16px;border-radius:4px;margin-bottom:16px">
        <b>O que são janelas deslizantes?</b><br>
        Para cada temporada T, calculamos a <b>média das últimas 3 e 5 temporadas anteriores</b>
        (ex.: para 2022 → média de 2019-2021 na janela de 3). Isso captura o <i>histórico recente</i>
        do clube sem vazar dados do futuro — o <code>shift(1)</code> garante que a temporada atual
        nunca entra no cálculo.
        </div>
        """, unsafe_allow_html=True)

        METRICAS_JAN = {
            "Pontos (Pts)": "Pts",
            "Saldo de Gols (SG)": "SG",
            "Gols Marcados": "Gols_Pro",
            "Gols Sofridos": "Gols_Contra",
            "Vitórias": "V",
            "Aproveitamento": "Aproveitamento",
        }

        df_desemp_jan = carregar_desempenho_com_janelas()

        j1, j2 = st.columns([1, 2])
        with j1:
            clube_jan = st.selectbox(
                "Selecione um clube",
                sorted(df_desemp_jan["Clube"].dropna().unique()),
                key="clube_jan"
            )
            metrica_label = st.selectbox(
                "Métrica", list(METRICAS_JAN.keys()), key="metrica_jan"
            )

        metrica_col = METRICAS_JAN[metrica_label]
        col_3 = f"{metrica_col}_media_3"
        col_5 = f"{metrica_col}_media_5"

        df_clube = (
            df_desemp_jan[df_desemp_jan["Clube"] == clube_jan]
            .sort_values("Temporada")
            .reset_index(drop=True)
        )

        with j2:
            fig_jan = px.line(
                df_clube,
                x="Temporada",
                y=[metrica_col, col_3, col_5],
                markers=True,
                template=_TEMPLATE,
                title=f"{clube_jan} — {metrica_label} com janelas deslizantes",
                labels={
                    metrica_col: "Valor real (temporada)",
                    col_3: "Média 3 temporadas anteriores",
                    col_5: "Média 5 temporadas anteriores",
                },
                color_discrete_map={
                    metrica_col: "#aaaaaa",
                    col_3: _AZUL,
                    col_5: _VERMELHO,
                },
            )
            fig_jan.update_layout(height=380, legend_title="Série")
            st.plotly_chart(fig_jan, use_container_width=True)

        st.markdown(f"**Tabela: {clube_jan} — {metrica_label}**")
        df_tabela = df_clube[["Clube", "Temporada", metrica_col, col_3, col_5]].rename(columns={
            metrica_col: "Valor Real",
            col_3: "Média 3 temporadas anteriores",
            col_5: "Média 5 temporadas anteriores",
        })
        st.dataframe(df_tabela.style.format(precision=2), use_container_width=True, height=320)

        st.caption(
            "Cada linha mostra o valor real da métrica naquele ano e as médias "
            "das temporadas **anteriores** (ex.: janela 3 em 2022 = média de 2019, 2020, 2021). "
            "Esses valores são as features usadas pelo modelo para prever o risco de rebaixamento."
        )

    st.markdown(
        '<div class="custom-footer">TCC · Leonardo Feitosa · Ciência de Dados – UFPB · 2025</div>',
        unsafe_allow_html=True,
    )
