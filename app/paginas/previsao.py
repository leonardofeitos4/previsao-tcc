import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.utils.processamento import fazer_previsao, carregar_dados_excel

# ── Paleta de cores consistente ──────────────────────────────────────────────
_AZUL      = "#1e3d59"
_VERMELHO  = "#e53935"
_VERDE     = "#27ae60"
_LARANJA   = "#f57c00"
_TEMPLATE  = "plotly_white"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _cor_e_classe(prob_reb: float):
    if prob_reb >= 0.6:
        return "result-danger", "🚨", "Alto risco de rebaixamento"
    if prob_reb >= 0.35:
        return "result-warning", "⚠️", "Risco moderado de rebaixamento"
    return "result-safe", "✅", "Baixo risco de rebaixamento"


def _donut(prob_reb: float) -> go.Figure:
    fig = go.Figure(go.Pie(
        values=[prob_reb, 1 - prob_reb],
        labels=["Rebaixamento", "Permanência"],
        hole=0.72,
        marker_colors=[_VERMELHO, _VERDE],
        textinfo="none",
        hovertemplate="%{label}: %{percent}<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{prob_reb:.1%}</b>",
        x=0.5, y=0.5, font_size=22, showarrow=False,
    )
    fig.update_layout(
        template=_TEMPLATE,
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )
    return fig


def _ranking_bar(df: pd.DataFrame) -> go.Figure:
    cores = [_VERMELHO if r == "Rebaixado" else _VERDE for r in df["Previsão"]]
    fig = go.Figure(go.Bar(
        x=df["Prob. Rebaixamento (%)"],
        y=df["Clube"],
        orientation="h",
        marker_color=cores,
        text=df["Prob. Rebaixamento (%)"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Prob. rebaixamento: %{x:.1f}%<extra></extra>",
    ))
    fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5,
                  annotation_text="50 %", annotation_position="top")
    fig.update_layout(
        template=_TEMPLATE,
        title=dict(text="Ranking de Risco de Rebaixamento — 2025", font_size=14, x=0),
        xaxis=dict(title="Probabilidade de Rebaixamento (%)", range=[0, 115]),
        yaxis=dict(title="", autorange="reversed"),
        height=620,
        margin=dict(l=160, r=20, t=50, b=40),
        plot_bgcolor="white",
    )
    return fig


# ── Página principal ──────────────────────────────────────────────────────────

def main():
    # Info card
    st.markdown("""
    <div class="info-box">
        Modelo de <b>Regressão Logística</b> treinado com dados do Transfermarkt (2014–2022) e
        validado em 2023–2024 &nbsp;(acurácia&nbsp;89&nbsp;%). As previsões são baseadas em
        <b>tamanho do elenco</b>, <b>nº de estrangeiros</b> e <b>valor de mercado total</b>.
    </div>
    """, unsafe_allow_html=True)

    tab_sim, tab_rank, tab_lote = st.tabs([
        "🔮  Simulador Individual",
        "🏆  Ranking 2025",
        "📤  Previsão em Lote (CSV)",
    ])

    # ── TAB 1: Simulador ─────────────────────────────────────────────────────
    with tab_sim:
        col_form, col_res = st.columns([1, 1], gap="large")

        with col_form:
            st.markdown('<p class="section-title">Dados do Clube</p>', unsafe_allow_html=True)
            with st.form("form_simulador"):
                nome = st.text_input("Nome do clube", value="Meu Time")
                plantel = st.slider(
                    "Tamanho do elenco", 15, 50, 25,
                    help="Média histórica na Série A: ~28 atletas",
                )
                estrangeiros = st.slider(
                    "Nº de estrangeiros", 0, 15, 3,
                    help="Média histórica na Série A: ~4 atletas",
                )
                valor = st.slider(
                    "Valor de mercado total (M€)", 5.0, 300.0, 50.0, step=5.0,
                    help="Média histórica na Série A: ~85 M€",
                )
                analisar = st.form_submit_button("Analisar Risco", use_container_width=True)

        with col_res:
            st.markdown('<p class="section-title">Resultado da Análise</p>', unsafe_allow_html=True)

            if analisar:
                entrada = pd.DataFrame({
                    "Plantel": [plantel],
                    "Estrangeiros": [estrangeiros],
                    "Valor de Mercado Total": [valor],
                })
                with st.spinner("Calculando..."):
                    _, probs = fazer_previsao(entrada)
                    prob_reb = probs[0][1]   # índice 1 → classe Rebaixado

                css_cls, emoji, mensagem = _cor_e_classe(prob_reb)

                st.markdown(f"""
                <div class="{css_cls}">
                    <p class="result-card-title">{nome}</p>
                    <p class="result-card-value">{prob_reb:.1%}</p>
                    <p class="result-card-sub">{emoji} {mensagem}</p>
                </div>
                """, unsafe_allow_html=True)

                st.plotly_chart(_donut(prob_reb), use_container_width=True)

                # Métricas nativas
                m1, m2, m3 = st.columns(3)
                m1.metric("Plantel", f"{plantel} atletas")
                m2.metric("Estrangeiros", f"{estrangeiros}")
                m3.metric("Valor de Mercado", f"{valor:.0f} M€")

                # Tabela comparativa
                st.markdown('<p class="section-title">Comparação com Referências</p>',
                            unsafe_allow_html=True)
                comp = pd.DataFrame({
                    "Clube": [nome, "Média Série A", "Rebaixado Típico", "Top-4 Típico"],
                    "Plantel": [plantel, 28, 24, 32],
                    "Estrangeiros": [estrangeiros, 4, 2, 7],
                    "Valor de Mercado (M€)": [valor, 85, 30, 150],
                    "Prob. Rebaixamento": [
                        f"{prob_reb:.1%}", "—", "~70 %", "~5 %"
                    ],
                })
                st.dataframe(comp, hide_index=True, use_container_width=True)

    # ── TAB 2: Ranking 2025 ───────────────────────────────────────────────────
    with tab_rank:
        st.markdown('<p class="section-title">Probabilidade de Rebaixamento — Temporada 2025</p>',
                    unsafe_allow_html=True)
        st.caption(
            "Os **4 clubes** com maior probabilidade de rebaixamento são destacados em vermelho. "
            "Dados baseados nos elencos/valores de mercado registrados para a temporada 2025."
        )

        try:
            df_base = carregar_dados_excel()
        except Exception as e:
            st.error(f"Erro ao carregar base de dados: {e}")
            return

        temp_max = df_base["Temporada"].max()
        df_2025 = df_base[df_base["Temporada"] == temp_max].copy()

        if df_2025.empty:
            st.warning("Nenhum dado encontrado para a temporada mais recente.")
            return

        _, probs_2025 = fazer_previsao(
            df_2025[["Plantel", "Estrangeiros", "Valor de Mercado Total"]]
        )

        df_rank = df_2025[["Clube"]].copy()
        df_rank["Prob. Rebaixamento (%)"] = [round(p[1] * 100, 2) for p in probs_2025]
        df_rank = df_rank.sort_values("Prob. Rebaixamento (%)", ascending=False).reset_index(drop=True)
        df_rank.index += 1
        df_rank["Previsão"] = "Permanece"
        df_rank.loc[df_rank.index <= 4, "Previsão"] = "Rebaixado"

        st.plotly_chart(_ranking_bar(df_rank), use_container_width=True)

        # Tabela estilizada
        def _estilo(row):
            if row["Previsão"] == "Rebaixado":
                return ["background-color:#fde8e8; color:#b91c1c; font-weight:600"] * len(row)
            return [""] * len(row)

        st.markdown("**Tabela completa**")
        df_show = df_rank[["Clube", "Prob. Rebaixamento (%)", "Previsão"]]
        st.dataframe(
            df_show.style.apply(_estilo, axis=1),
            use_container_width=True,
            height=600,
        )

        # Download
        csv_bytes = df_show.to_csv(index=True).encode("utf-8")
        st.download_button(
            "📥 Baixar tabela (CSV)",
            data=csv_bytes,
            file_name="previsao_rebaixamento_2025.csv",
            mime="text/csv",
        )

    # ── TAB 3: Lote CSV ───────────────────────────────────────────────────────
    with tab_lote:
        st.markdown('<p class="section-title">Previsão em Lote via Arquivo CSV</p>',
                    unsafe_allow_html=True)

        template_df = pd.DataFrame({
            "Clube":                ["Clube A", "Clube B"],
            "Plantel":              [28, 24],
            "Estrangeiros":         [4, 2],
            "Valor de Mercado Total": [85.0, 30.0],
        })
        csv_buf = io.StringIO()
        template_df.to_csv(csv_buf, index=False)

        c1, c2 = st.columns([1, 2])
        with c1:
            st.download_button(
                "📥 Baixar template CSV",
                data=csv_buf.getvalue().encode("utf-8"),
                file_name="template_clubes.csv",
                mime="text/csv",
            )
        with c2:
            st.caption("O arquivo deve conter as colunas: `Clube`, `Plantel`, `Estrangeiros`, `Valor de Mercado Total`")

        with st.expander("Ver exemplo de formato"):
            st.dataframe(template_df, use_container_width=True, hide_index=True)

        uploaded = st.file_uploader("Faça upload do arquivo CSV", type=["csv"])
        if uploaded:
            try:
                df_up = pd.read_csv(uploaded)
                st.markdown("**Pré-visualização dos dados enviados:**")
                st.dataframe(df_up.head(), use_container_width=True, hide_index=True)

                with st.spinner("Gerando previsões..."):
                    _, probs_up = fazer_previsao(
                        df_up[["Plantel", "Estrangeiros", "Valor de Mercado Total"]]
                    )
                    df_up["Prob. Rebaixamento (%)"] = [round(p[1] * 100, 1) for p in probs_up]
                    df_up["Previsão"] = [
                        "Rebaixado" if p[1] > 0.5 else "Permanece" for p in probs_up
                    ]

                st.success(f"{len(df_up)} clube(s) analisado(s).")
                st.dataframe(df_up, use_container_width=True, hide_index=True)

                if len(df_up) > 1:
                    fig_b = px.bar(
                        df_up.sort_values("Prob. Rebaixamento (%)", ascending=False),
                        x="Clube" if "Clube" in df_up.columns else df_up.index.astype(str),
                        y="Prob. Rebaixamento (%)",
                        color="Previsão",
                        color_discrete_map={"Rebaixado": _VERMELHO, "Permanece": _VERDE},
                        template=_TEMPLATE,
                        title="Probabilidade de Rebaixamento — Clubes do Arquivo",
                    )
                    st.plotly_chart(fig_b, use_container_width=True)

                csv_out = df_up.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Baixar resultado (CSV)", csv_out,
                                   "resultado_previsao.csv", "text/csv")
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")

    st.markdown(
        '<div class="custom-footer">TCC · Leonardo Feitosa · Ciência de Dados – UFPB · 2025</div>',
        unsafe_allow_html=True,
    )
