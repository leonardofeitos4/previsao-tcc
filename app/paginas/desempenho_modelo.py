"""
Tela: Desempenho do Modelo
Avaliação séria: matriz de confusão, ROC, calibração, comparação de algoritmos,
odds ratios — todos calculados com dados reais do modelo treinado.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_curve, auc, confusion_matrix,
)
from sklearn.calibration import calibration_curve

from app.utils.processamento import carregar_dados_excel, carregar_modelo, FEATURES, FEATURES_JANELA
from app.utils.styles import (
    GREEN, RED, AMBER, BLUE, VIOLET, MUTED, FAINT,
    SURF, SURF2, SURF3, BORDER, TEXT, PLOTLY_LAYOUT,
)

# ── dados comparação walk-forward (notebooks 06) ─────────────────────────────
_MODELOS_COMP = [
    {"nome": "LightGBM",            "sigla": "LGB", "auc_cv": 0.700, "auc_teste": 0.877, "acc": 0.825, "f1": 0.65, "escolhido": False, "nota": "Melhor AUC no teste, porém alta variância (±0.151)"},
    {"nome": "Random Forest",       "sigla": "RF",  "auc_cv": 0.762, "auc_teste": 0.844, "acc": 0.800, "f1": 0.60, "escolhido": False, "nota": "Bom AUC; menos interpretável"},
    {"nome": "Regressão Logística", "sigla": "LR",  "auc_cv": 0.794, "auc_teste": 0.828, "acc": 0.800, "f1": 0.59, "escolhido": True,  "nota": "Melhor estabilidade walk-forward (±0.058) + interpretável"},
    {"nome": "XGBoost",             "sigla": "XGB", "auc_cv": 0.659, "auc_teste": 0.652, "acc": 0.825, "f1": 0.55, "escolhido": False, "nota": "Alta acurácia mas AUC baixo — viés para classe majoritária"},
]


@st.cache_data(show_spinner=False)
def _computar_metricas():
    df  = carregar_dados_excel()
    modelo, scaler, mediana = carregar_modelo()

    df_te = df[(df["Temporada"] > 2022) & (df["Temporada"] < 2025)].copy()
    if mediana is not None:
        for col in FEATURES_JANELA:
            if col in df_te.columns:
                df_te[col] = df_te[col].fillna(mediana[col])
            else:
                df_te[col] = mediana[col]

    X_te = scaler.transform(df_te[FEATURES])
    y_te = df_te["Status_bin"].values
    y_pred = modelo.predict(X_te)
    y_prob = modelo.predict_proba(X_te)[:, 1]

    cm = confusion_matrix(y_te, y_pred)
    tn, fp, fn, tp = cm.ravel()

    fpr_arr, tpr_arr, _ = roc_curve(y_te, y_prob)
    roc_auc = auc(fpr_arr, tpr_arr)

    prob_true, prob_pred = calibration_curve(y_te, y_prob, n_bins=6, strategy="quantile")

    coefs   = modelo.coef_[0]
    odds_rs = np.exp(coefs)
    feat_labels = [f.replace("_media_", " média ").replace("_", " ") for f in FEATURES]
    idx_sort = np.argsort(np.abs(np.log(odds_rs)))[::-1]

    return {
        "acc":      accuracy_score(y_te, y_pred),
        "prec":     precision_score(y_te, y_pred, zero_division=0),
        "rec":      recall_score(y_te, y_pred, zero_division=0),
        "f1":       f1_score(y_te, y_pred, zero_division=0),
        "roc_auc":  roc_auc,
        "cm":       {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "fpr":      fpr_arr.tolist(),
        "tpr":      tpr_arr.tolist(),
        "calib_x":  prob_pred.tolist(),
        "calib_y":  prob_true.tolist(),
        "or_feats": [feat_labels[i] for i in idx_sort],
        "or_vals":  [float(odds_rs[i]) for i in idx_sort],
    }


def _roc_chart(m: dict) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines",
                             line=dict(dash="dash", color=MUTED, width=1.2),
                             name="Aleatório", showlegend=True))
    fig.add_trace(go.Scatter(
        x=m["fpr"], y=m["tpr"], mode="lines",
        line=dict(color=GREEN, width=2.5),
        fill="tozeroy", fillcolor="rgba(51,196,106,.12)",
        name=f'AUC = {m["roc_auc"]:.3f}',
    ))
    layout = dict(**PLOTLY_LAYOUT)
    layout.update(
        height=300, margin=dict(l=30, r=16, t=30, b=30),
        xaxis=dict(title="Taxa de Falso Positivo", range=[0, 1],
                   gridcolor="rgba(255,255,255,.06)", color=MUTED),
        yaxis=dict(title="Taxa de Verdadeiro Positivo", range=[0, 1],
                   gridcolor="rgba(255,255,255,.06)", color=MUTED),
        legend=dict(x=0.6, y=0.1, font=dict(color=MUTED, size=12)),
        title=dict(text="Curva ROC", font=dict(size=13, color=TEXT)),
    )
    fig.update_layout(**layout)
    return fig


def _calib_chart(m: dict) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines",
                             line=dict(dash="dash", color=MUTED, width=1.2),
                             name="Ideal"))
    fig.add_trace(go.Scatter(
        x=m["calib_x"], y=m["calib_y"], mode="lines+markers",
        line=dict(color=BLUE, width=2.5),
        marker=dict(size=7, color=BLUE),
        name="Modelo",
    ))
    layout = dict(**PLOTLY_LAYOUT)
    layout.update(
        height=300, margin=dict(l=30, r=16, t=30, b=30),
        xaxis=dict(title="Probabilidade prevista", range=[0, 1],
                   gridcolor="rgba(255,255,255,.06)", color=MUTED),
        yaxis=dict(title="Fração observada", range=[0, 1],
                   gridcolor="rgba(255,255,255,.06)", color=MUTED),
        legend=dict(x=0.05, y=0.9, font=dict(color=MUTED, size=12)),
        title=dict(text="Calibração", font=dict(size=13, color=TEXT)),
    )
    fig.update_layout(**layout)
    return fig


def _odds_chart(m: dict) -> go.Figure:
    feats = m["or_feats"][:10]  # top-10
    ors   = m["or_vals"][:10]
    colors = [RED if v > 1 else GREEN for v in ors]
    fig = go.Figure(go.Bar(
        x=[v - 1 for v in ors],
        y=feats,
        orientation="h",
        base=[1] * len(feats),
        marker_color=colors,
        marker_opacity=0.85,
        text=[f"{v:.2f}" for v in ors],
        textposition="outside",
        textfont=dict(color=MUTED, size=11),
        hovertemplate="<b>%{y}</b><br>OR = %{text}<extra></extra>",
    ))
    fig.add_vline(x=1, line_color=MUTED, line_width=1.2, opacity=0.6,
                  annotation_text="1,0", annotation_font_color=MUTED)
    layout = dict(**PLOTLY_LAYOUT)
    layout.update(
        height=360, margin=dict(l=10, r=80, t=30, b=30),
        xaxis=dict(title="Odds Ratio", gridcolor="rgba(255,255,255,.06)", color=MUTED),
        yaxis=dict(color=MUTED),
        title=dict(text="Odds Ratios dos coeficientes (OR < 1 = protege; > 1 = aumenta risco)",
                   font=dict(size=12, color=TEXT)),
    )
    fig.update_layout(**layout)
    return fig


def main():
    # ── Hero ──
    st.markdown("""
    <div class="hero" style="padding:20px 28px 24px;">
      <div class="hero-tag">Avaliação · Machine Learning</div>
      <h1 style="font-size:1.55rem;">Desempenho do Modelo</h1>
      <p>Métricas completas: matriz de confusão, curva ROC, calibração e odds ratios — dados reais do conjunto de teste 2023–2024.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="callout">
      Em rebaixamento as classes são desbalanceadas (~20% positivos), então a
      <b>acurácia sozinha engana</b>. Por isso reportamos <b>precisão, recall, F1, ROC e calibração</b> —
      o <b>recall da classe "rebaixado"</b> é a métrica que mais importa operacionalmente.
    </div>
    """, unsafe_allow_html=True)

    try:
        m = _computar_metricas()
    except Exception as e:
        st.error(f"Erro ao calcular métricas: {e}")
        return

    # ── 6 KPI cards ──
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    cards = [
        (c1, "Acurácia",             f"{m['acc']*100:.1f}",  "%",       None,  "teste 2023–24"),
        (c2, "Precisão",             f"{m['prec']:.2f}",    "",        BLUE,  "dos previstos, quantos caíram"),
        (c3, "Recall (rebaixado)",   f"{m['rec']:.2f}",     "",        GREEN, "dos que caíram, quantos achamos"),
        (c4, "F1-Score",             f"{m['f1']:.2f}",      "",        AMBER, "equilíbrio precisão×recall"),
        (c5, "AUC-ROC (teste)",      f"{m['roc_auc']:.3f}", "",        None,  "conjunto de teste"),
        (c6, "AUC-ROC (walk-fwd)",   "0,794",               "",        None,  "± 0,058 · 5 folds"),
    ]
    for col, label, val, unit, color, sub in cards:
        color_style = f"color:{color};" if color else ""
        col.markdown(f"""
        <div class="stat-card">
          <div class="stat-label">{label}</div>
          <div class="stat-value" style="{color_style}">{val}<span class="stat-unit">{unit}</span></div>
          <div class="stat-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Matriz de confusão + ROC + Calibração ──
    col_cm, col_roc, col_cal = st.columns(3)

    with col_cm:
        st.markdown("""
        <div style="background:#141a1f;border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:18px;">
          <div style="font-size:12px;font-weight:600;color:#8b98a4;margin-bottom:14px;">
            Matriz de Confusão
          </div>""", unsafe_allow_html=True)

        cm = m["cm"]
        total = sum(cm.values())
        cells = [
            (cm["tn"], "Verd. Negativo", True),
            (cm["fp"], "Falso Positivo",  False),
            (cm["fn"], "Falso Negativo",  False),
            (cm["tp"], "Verd. Positivo",  True),
        ]

        def _opacity(v):
            return 0.35 + 0.65 * (v / total)

        def _cf_cell(v, label, good):
            bg  = f"rgba(51,196,106,{_opacity(v):.2f})" if good else f"rgba(240,82,75,{_opacity(v):.2f})"
            brd = "rgba(51,196,106,.35)" if good else "rgba(240,82,75,.35)"
            return (
                f'<div class="cf-cell" style="background:{bg};border:1px solid {brd};">'
                f'<span class="cf-num">{v}</span>'
                f'<span class="cf-lbl">{label}</span>'
                f'</div>'
            )

        st.markdown(f"""
          <div class="cf-grid">
            <div class="cf-corner"></div>
            <div class="cf-coltop">Previsto: Permanece</div>
            <div class="cf-coltop">Previsto: Rebaixado</div>
            <div class="cf-rowside">Real: Permanece</div>
            {_cf_cell(cm["tn"],"Verd. Negativo",True)}
            {_cf_cell(cm["fp"],"Falso Positivo",False)}
            <div class="cf-rowside">Real: Rebaixado</div>
            {_cf_cell(cm["fn"],"Falso Negativo",False)}
            {_cf_cell(cm["tp"],"Verd. Positivo",True)}
          </div>
          <div style="font-size:11px;color:#5e6b77;margin-top:10px;line-height:1.5;">
            Opacidade proporcional ao número de casos.
          </div>
        </div>""", unsafe_allow_html=True)

    with col_roc:
        st.plotly_chart(_roc_chart(m), use_container_width=True)

    with col_cal:
        st.plotly_chart(_calib_chart(m), use_container_width=True)
        st.markdown(
            '<p style="font-size:11px;color:#5e6b77;margin-top:-10px;">'
            'Pontos próximos da diagonal = probabilidades confiáveis.</p>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Comparação de algoritmos ──
    st.markdown('<div class="sec-kicker">Comparação</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-h2">Por que Regressão Logística?</div>', unsafe_allow_html=True)

    rows_html = ""
    for algo in _MODELOS_COMP:
        row_cls  = "comp-row comp-row-on" if algo["escolhido"] else "comp-row"
        check    = "✓ " if algo["escolhido"] else ""
        name_col = f'<b style="color:#33c46a;">{check}{algo["nome"]}</b>' if algo["escolhido"] else algo["nome"]
        rows_html += f"""
        <tr class="{row_cls}">
          <td>{name_col} <em style="color:#5e6b77;font-size:11px;">{algo['sigla']}</em></td>
          <td class="comp-mono">{algo['auc_cv']:.3f}</td>
          <td class="comp-mono">{algo['auc_teste']:.3f}</td>
          <td class="comp-mono">{algo['acc']*100:.1f}%</td>
          <td class="comp-mono">{algo['f1']:.2f}</td>
          <td class="comp-note">{algo['nota']}</td>
        </tr>"""

    st.markdown(f"""
    <div style="background:#141a1f;border:1px solid rgba(255,255,255,.08);border-radius:14px;overflow:hidden;margin-bottom:24px;">
      <table class="comp-table">
        <thead class="comp-head">
          <tr>
            <th>Algoritmo</th>
            <th>AUC-ROC (walk-fwd)</th>
            <th>AUC-ROC (teste)</th>
            <th>Acurácia</th>
            <th>F1</th>
            <th>Observação</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

    # ── Odds Ratios ──
    st.markdown('<div class="sec-kicker">Interpretabilidade</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-h2">Coeficientes — Odds Ratios</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="callout callout-muted">
      Odds ratio &lt; 1 = a variável <b>reduz</b> a chance de rebaixamento;
      &gt; 1 = <b>aumenta</b>. Barras verdes protegem; vermelhas agravam.
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(_odds_chart(m), use_container_width=True)

    st.markdown('<div class="app-footer">TCC · Leonardo Feitosa · Ciência de Dados – UFPB · 2025</div>',
                unsafe_allow_html=True)
