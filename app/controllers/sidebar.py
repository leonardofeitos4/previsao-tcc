import streamlit as st


_NAV_OPTIONS = {
    "Previsao":             "Previsão 2025",
    "Ranking":              "Ranking 2025",
    "Desempenho":           "Desempenho do Modelo",
    "Dados Historicos":     "Dados Históricos",
    "Sensibilidade":        "Análise de Sensibilidade",
    "Descritiva":           "Análise Descritiva",
}

_NAV_NEW = {"Ranking", "Desempenho"}


def streamlit_menu() -> str:
    with st.sidebar:
        st.markdown("""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;">
  <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(150deg,#1f7a44,#0f3d23);
       display:flex;align-items:center;justify-content:center;font-size:18px;
       box-shadow:0 0 0 1px rgba(51,196,106,.3);">⚽</div>
  <div>
    <div style="font-family:'IBM Plex Sans',sans-serif;font-weight:700;font-size:15px;color:#eef2f5;">Série A 2025</div>
    <div style="font-size:11px;color:#8b98a4;">Previsão de Rebaixamento</div>
  </div>
</div>
<p class="sb-label">Navegação</p>
""", unsafe_allow_html=True)

        selected = st.radio(
            label="nav",
            options=list(_NAV_OPTIONS.keys()),
            format_func=lambda k: ("🆕 " if k in _NAV_NEW else "") + _NAV_OPTIONS[k],
            label_visibility="collapsed",
        )
    return selected


def sidebar_content() -> None:
    st.sidebar.markdown('<p class="sb-label">Sobre o Modelo</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
<div class="mm-card">
  <div class="mm-row"><span>Algoritmo</span><b>Reg. Logística</b></div>
  <div class="mm-row"><span>Treino</span><b>2014 – 2022</b></div>
  <div class="mm-row"><span>Teste</span><b>2023 – 2024</b></div>
  <div class="mm-row"><span>Acurácia (teste)</span><b>80,0 %</b></div>
  <div class="mm-row"><span>AUC-ROC (teste)</span><b>0,828</b></div>
  <div class="mm-row"><span>AUC-ROC (walk-forward)</span><b>0,794 ± 0,058</b></div>
  <div class="mm-row"><span>Validação</span><b>Walk-forward (5 folds)</b></div>
  <div class="mm-row"><span>Modelos testados</span><b>LR · RF · XGB · LGB</b></div>
  <div class="mm-feat">
    <div style="font-size:11.5px;color:#8b98a4;margin-bottom:7px;font-weight:600;">15 features</div>
    <span class="mm-tag">Plantel</span>
    <span class="mm-tag">Estrangeiros</span>
    <span class="mm-tag">Valor de mercado</span>
    <span class="mm-tag">12 janelas deslizantes</span>
  </div>
</div>
""", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<p style="font-size:10.5px;color:#5e6b77;line-height:1.5;">'
        'TCC · Leonardo Feitosa · Ciência de Dados – UFPB · 2025</p>',
        unsafe_allow_html=True,
    )
