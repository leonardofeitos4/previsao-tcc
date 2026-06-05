"""
Tela: Ranking 2025
Exibe os 20 clubes ordenados pela probabilidade real de rebaixamento.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from app.utils.processamento import carregar_dados_excel, fazer_previsao
from app.utils.styles import GREEN, RED, AMBER, LIME, MUTED, SURF, SURF2, SURF3, PLOTLY_LAYOUT

# cores fixas dos clubes (fallback = cinza)
_CORES_CLUBE = {
    "Flamengo":      "#E03A3E",
    "Palmeiras":     "#1B7A3D",
    "Botafogo":      "#3a3a3a",
    "São Paulo":     "#E03A3E",
    "Sao Paulo":     "#E03A3E",
    "Corinthians":   "#3a3a3a",
    "Atletico Mineiro": "#3a3a3a",
    "Atlético Mineiro": "#3a3a3a",
    "Internacional": "#E03A3E",
    "Cruzeiro":      "#1A3B8B",
    "Vasco da Gama": "#3a3a3a",
    "Gremio":        "#1A6BB5",
    "Grêmio":        "#1A6BB5",
    "Fluminense":    "#7A1F2B",
    "Bahia":         "#1A6BB5",
    "Bragantino":    "#E03A3E",
    "Santos":        "#3a3a3a",
    "Fortaleza":     "#1A3B8B",
    "Vitoria":       "#E03A3E",
    "Vitória":       "#E03A3E",
    "Ceara":         "#3a3a3a",
    "Ceará":         "#3a3a3a",
    "Juventude":     "#1B7A3D",
    "Sport Recife":  "#E03A3E",
    "Sport":         "#E03A3E",
    "Mirassol":      "#1B7A3D",
    "Atletico Goianiense": "#E03A3E",
}


def _risk_color(p: float) -> str:
    if p >= 0.50: return RED
    if p >= 0.30: return AMBER
    if p >= 0.15: return LIME
    return GREEN


def _risk_label(p: float) -> str:
    if p >= 0.50: return "danger"
    if p >= 0.30: return "warn"
    if p >= 0.15: return "lime"
    return "ok"


def _risk_text(p: float) -> str:
    if p >= 0.50: return "Risco alto"
    if p >= 0.30: return "Risco moderado"
    if p >= 0.15: return "Atenção"
    return "Risco baixo"


def _initials(nome: str) -> str:
    words = [w for w in nome.split() if len(w) > 2]
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return nome.replace(" ", "")[:2].upper()


def _crest_html(nome: str, size: int = 28) -> str:
    cor = _CORES_CLUBE.get(nome, "#3a3a3a")
    ini = _initials(nome)
    fs  = int(size * 0.38)
    return (
        f'<span class="crest" style="width:{size}px;height:{size}px;'
        f'background:{cor};font-size:{fs}px;">{ini}</span>'
    )


def _probbar_html(p: float, height: int = 10) -> str:
    cor = _risk_color(p)
    pct = min(100, p * 100)
    return (
        f'<div class="probbar-wrap" style="height:{height}px;">'
        f'<div class="probbar-fill" style="width:{pct:.1f}%;background:{cor};"></div>'
        f'</div>'
    )


@st.cache_data(show_spinner=False)
def _build_ranking() -> pd.DataFrame:
    df = carregar_dados_excel()
    temp_max = df["Temporada"].max()
    df_2025  = df[df["Temporada"] == temp_max].copy()

    _, probs = fazer_previsao(df_2025)
    df_2025["prob_reb"] = [p[1] for p in probs]
    df_2025 = df_2025.sort_values("prob_reb", ascending=False).reset_index(drop=True)
    df_2025.index += 1
    return df_2025


def _bar_chart(df: pd.DataFrame) -> go.Figure:
    cores = [_risk_color(p) for p in df["prob_reb"]]
    fig = go.Figure(go.Bar(
        x=df["prob_reb"] * 100,
        y=df["Clube"],
        orientation="h",
        marker_color=cores,
        text=[f"{p*100:.1f}%" for p in df["prob_reb"]],
        textposition="outside",
        textfont=dict(color=MUTED, size=11),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>",
    ))
    fig.add_vline(x=50, line_dash="dash", line_color=RED,
                  line_width=1.2, opacity=0.5,
                  annotation_text="50 %", annotation_font_color=MUTED,
                  annotation_position="top")
    layout = dict(**PLOTLY_LAYOUT)
    layout.update(
        height=580,
        margin=dict(l=10, r=80, t=30, b=10),
        xaxis=dict(title="Probabilidade de rebaixamento (%)", range=[0, 120],
                   gridcolor="rgba(255,255,255,.06)", color=MUTED),
        yaxis=dict(autorange="reversed", color=MUTED),
        title=dict(text="Ranking de Risco — Brasileirão Série A 2025",
                   font=dict(size=14, color="#eef2f5")),
    )
    fig.update_layout(**layout)
    return fig


def main():
    # ── Hero ──
    st.markdown("""
    <div class="hero" style="padding:20px 28px 24px;">
      <div class="hero-tag">Projeção do modelo · 20 clubes</div>
      <h1 style="font-size:1.55rem;">Ranking de Risco de Rebaixamento <span class="hero-em">2025</span></h1>
      <p>Probabilidades reais calculadas pelo modelo de Regressão Logística treinado em 2014–2024.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="callout callout-warn">
      <strong>Leitura:</strong> probabilidade individual de rebaixamento estimada pelo modelo a partir
      do elenco e do desempenho recente de cada clube.
      Os <b>4 primeiros</b> formam a zona de rebaixamento projetada (fundo vermelho).
    </div>
    """, unsafe_allow_html=True)

    try:
        df = _build_ranking()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return

    n = len(df)
    media = df["prob_reb"].mean()
    mais_seguro = df.iloc[-1]

    # ── KPIs ──
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""
    <div class="stat-card">
      <div class="stat-label">Clubes analisados</div>
      <div class="stat-value">{n}</div>
    </div>""", unsafe_allow_html=True)
    k2.markdown(f"""
    <div class="stat-card">
      <div class="stat-label">Risco médio da liga</div>
      <div class="stat-value" style="color:{AMBER};">{media*100:.1f}<span class="stat-unit">%</span></div>
    </div>""", unsafe_allow_html=True)
    k3.markdown(f"""
    <div class="stat-card">
      <div class="stat-label">Zona de rebaixamento</div>
      <div class="stat-value" style="color:{RED};">4<span class="stat-unit">clubes</span></div>
    </div>""", unsafe_allow_html=True)
    k4.markdown(f"""
    <div class="stat-card">
      <div class="stat-label">Mais seguro</div>
      <div class="stat-value" style="font-size:1.2rem;color:{GREEN};">{mais_seguro['Clube']}</div>
      <div class="stat-sub">{mais_seguro['prob_reb']*100:.1f}% de risco</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabela ranking ──
    rows_html = ""
    for pos, row in df.iterrows():
        zona   = pos <= 4
        num_class = "rk-num-zone" if zona else "rk-num"
        row_class = "rank-zone" if zona else "rank-row"
        p      = row["prob_reb"]
        cor    = _risk_color(p)
        label  = _risk_text(p)
        badge_cls = f"badge-{_risk_label(p)}"

        # VM total (pode não existir se não vier do excel)
        vm_val = row.get("Valor de Mercado Total", None)
        vm_str = f"{vm_val:.0f}" if vm_val and vm_val > 0 else "—"

        rows_html += f"""
        <tr class="{row_class}">
          <td><span class="{num_class}">{pos}</span></td>
          <td>
            {_crest_html(row['Clube'], 26)}
            <span class="rk-name" style="margin-left:9px;">{row['Clube']}</span>
          </td>
          <td style="min-width:160px;">{_probbar_html(p, 10)}</td>
          <td><span class="rk-mono" style="color:{cor};">{p*100:.1f}%</span></td>
          <td><span class="badge {badge_cls}">{label}</span></td>
          <td><span class="rk-muted">{vm_str} M€</span></td>
        </tr>"""

    st.markdown(f"""
    <div style="background:#141a1f;border:1px solid rgba(255,255,255,.08);border-radius:14px;overflow:hidden;">
      <table class="rank-table">
        <thead class="rank-head">
          <tr>
            <th>#</th><th>Clube</th><th>Probabilidade</th>
            <th>Risco</th><th>Faixa</th><th>VM (M€)</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
      <div style="display:flex;align-items:center;gap:7px;justify-content:center;
           font-size:11.5px;color:#5e6b77;padding:12px;
           background:#1a212a;border-top:1px dashed rgba(240,82,75,.3);">
        ✂ linha de corte — 4º / 5º colocado projetado
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(_bar_chart(df), use_container_width=True)

    st.markdown("""
    <div class="callout callout-muted">
      Projeção ilustrativa para fins acadêmicos — não constitui aposta ou previsão oficial.
      Probabilidades individuais; a soma não é normalizada para exatamente 4.
    </div>
    """, unsafe_allow_html=True)

    # Download
    csv = df[["Clube", "prob_reb"]].rename(columns={"prob_reb": "Prob. Rebaixamento"})
    csv["Prob. Rebaixamento (%)"] = (csv["Prob. Rebaixamento"] * 100).round(2)
    csv["Previsão"] = csv.index.map(lambda i: "Rebaixado" if i <= 4 else "Permanece")
    st.download_button(
        "Baixar ranking (CSV)",
        csv[["Clube", "Prob. Rebaixamento (%)", "Previsão"]].to_csv(index=False).encode(),
        "ranking_rebaixamento_2025.csv",
        "text/csv",
    )

    st.markdown('<div class="app-footer">TCC · Leonardo Feitosa · Ciência de Dados – UFPB · 2025</div>',
                unsafe_allow_html=True)
