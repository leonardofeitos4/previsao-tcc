import streamlit as st
from app.utils.styles import apply_custom_css


def set_page_configuration():
    st.set_page_config(
        page_title="Previsão Rebaixamento – Série A 2025",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_css()


def show_title():
    st.markdown("""
    <div class="hero">
      <div class="hero-tag">Análise preditiva · Machine Learning</div>
      <h1>Previsão de Rebaixamento<span class="hero-em"> — Brasileirão Série A 2025</span></h1>
      <p>Regressão Logística · Leonardo Feitosa — Ciência de Dados · UFPB</p>
    </div>
    """, unsafe_allow_html=True)
