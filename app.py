"""
app.py
------
Ponto de entrada do aplicativo Streamlit — Previsao de Rebaixamento
no Brasileirao Serie A 2025.

Estrutura do projeto:
    app/controllers/ — configuracao e menu lateral
    app/paginas/     — paginas do aplicativo
    app/utils/       — processamento, modelos e estilos

Autor: Leonardo Feitosa — Ciencia de Dados / UFPB
"""

import os
import sys

# Garante que o diretorio raiz do projeto esteja no path de importacao
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.controllers.config import set_page_configuration, show_title
from app.controllers.sidebar import streamlit_menu, sidebar_content

from app.paginas.previsao import main as main_previsao
from app.paginas.dados_historicos import main as main_dados
from app.paginas.analise_sensibilidade import main as main_analise
from app.paginas.analise_descritiva import main as main_descritiva

# Configuracao de pagina — deve vir antes de qualquer outro st.*
set_page_configuration()
show_title()

# Menu lateral
selected_option = streamlit_menu()

# Roteamento de paginas
if selected_option == "Previsao":
    main_previsao()
elif selected_option == "Dados Historicos":
    main_dados()
elif selected_option == "Analise de Sensibilidade":
    main_analise()
elif selected_option == "Analise Descritiva":
    main_descritiva()

# Conteudo fixo da barra lateral
sidebar_content()
