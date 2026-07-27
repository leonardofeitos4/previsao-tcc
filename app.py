"""
app.py  —  Previsão de Rebaixamento · Brasileirão Série A 2025
Gera o app React com dados reais e o serve via Streamlit.
"""
import os, sys
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

st.set_page_config(
    page_title="Previsão Rebaixamento · Série A 2025",
    page_icon="⚽",
    layout="wide",
)

# Oculta todo o chrome do Streamlit — o app é o HTML
st.markdown("""
<style>
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
.main,.block-container{padding:0!important;max-width:100%!important;}
iframe{border:none!important;}
</style>
""", unsafe_allow_html=True)

HTML_PATH = os.path.join(os.path.dirname(__file__), "previsao_rebaixamento.html")

# Gera o HTML com dados reais (se ainda não existe ou usuário pede regenerar)
need_gen = not os.path.exists(HTML_PATH)

if need_gen:
    with st.spinner("Gerando app com dados reais do modelo..."):
        from gerar_app_real import gerar
        gerar()

# Servir o HTML
with open(HTML_PATH, encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=900, scrolling=True)
