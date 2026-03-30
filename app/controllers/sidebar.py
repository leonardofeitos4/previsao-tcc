"""
controllers/sidebar.py
----------------------
Menu de navegação lateral e informações sobre o modelo.

Autor: Leonardo Feitosa — Ciência de Dados / UFPB
"""

import streamlit as st


def streamlit_menu() -> str:
    """Cria o menu de navegação lateral com 4 opções."""
    with st.sidebar:
        st.title("🔀 Menu Principal")
        selected = st.radio(
            label="",
            options=[
                "Previsao",
                "Dados Historicos",
                "Analise de Sensibilidade",
                "Analise Descritiva"
            ],
            format_func=lambda x: f"📊 {x}"
        )
    return selected


def sidebar_content() -> None:
    """Exibe informações sobre o modelo e o autor na barra lateral."""
    st.sidebar.markdown("---")
    st.sidebar.title("📌 Sobre o Modelo")
    st.sidebar.markdown("""
**Tipo:** Regressão Logística

**Features utilizadas:**
- Tamanho do Plantel (nº de atletas)
- Número de Estrangeiros
- Valor de Mercado Total (M€)

**Separação treino / teste:**
- Treino: 2014 – 2022
- Teste : 2023 – 2024
*(separação por período temporal, não aleatória)*

**Métricas no conjunto de teste:**
- Acurácia: **0.89**
- MAE: **0.11**
- RMSE: **0.32**

**Limitações:**
O modelo é baseado em dados históricos e não captura fatores externos como lesões, troca de comissão técnica ou calendário.
    """)
    st.sidebar.markdown("---")
    st.sidebar.markdown("👤 **Leonardo Feitosa**  \n📚 Ciência de Dados – UFPB")
