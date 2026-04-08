import streamlit as st


_NAV_OPTIONS = {
    "Previsao":                 ("🔮", "Previsão 2025"),
    "Dados Historicos":         ("📂", "Dados Históricos"),
    "Analise de Sensibilidade": ("🎚️", "Análise de Sensibilidade"),
    "Analise Descritiva":       ("📊", "Análise Descritiva"),
}


def streamlit_menu() -> str:
    with st.sidebar:
        st.markdown("## ⚽ Série A 2025")
        st.markdown('<p class="sidebar-section-title">Navegação</p>', unsafe_allow_html=True)

        selected = st.radio(
            label="Navegação",
            options=list(_NAV_OPTIONS.keys()),
            format_func=lambda k: f"{_NAV_OPTIONS[k][0]}  {_NAV_OPTIONS[k][1]}",
            label_visibility="collapsed",
        )
    return selected


def sidebar_content() -> None:
    st.sidebar.markdown("---")

    st.sidebar.markdown('<p class="sidebar-section-title">Sobre o Modelo</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
<div class="sidebar-metric">
  <span class="sidebar-metric-label">Algoritmo</span>
  <span class="sidebar-metric-value">Reg. Logística</span>
</div>
<div class="sidebar-metric">
  <span class="sidebar-metric-label">Treino</span>
  <span class="sidebar-metric-value">2014 – 2022</span>
</div>
<div class="sidebar-metric">
  <span class="sidebar-metric-label">Teste</span>
  <span class="sidebar-metric-value">2023 – 2024</span>
</div>
<div class="sidebar-metric">
  <span class="sidebar-metric-label">Acurácia (teste)</span>
  <span class="sidebar-metric-value">77,5 %</span>
</div>
<div class="sidebar-metric">
  <span class="sidebar-metric-label">AUC-ROC</span>
  <span class="sidebar-metric-value">0.82</span>
</div>
""", unsafe_allow_html=True)

    st.sidebar.markdown('<p class="sidebar-section-title">Features</p>', unsafe_allow_html=True)
    st.sidebar.markdown("""
- 👥 Tamanho do plantel
- 🌍 Nº de estrangeiros
- 💶 Valor de mercado total
""")

    st.sidebar.markdown("---")
    st.sidebar.caption("👤 **Leonardo Feitosa**  \n📚 Ciência de Dados – UFPB  \n🗓️ 2025")
