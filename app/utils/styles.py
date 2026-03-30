import streamlit as st

# Essa função retorna uma string com vários estilos CSS customizados:
# Ela permite personalizar visualmente elementos padrão do Streamlit e
# criar uma identidade visual mais profissional para seu app.
def load_css():
    return """
    <style>
        /* Estilo para headers principais */
        .main-header {
            font-size: 2.5rem;
            color: #1e3d59;
            text-align: center;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Estilo para subtítulos */
        .subheader {
            font-size: 1.8rem;
            color: #1e3d59;
            margin-top: 2rem;
            border-bottom: 2px solid #f5f0e1;
            padding-bottom: 0.5rem;
        }
        
        /* Estiliza os cards usados para boxes explicativos/painéis */
        .card {
            background-color: #f5f0e1;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        /* Valor principal de métrica (ex: percentual de rebaixamento) */
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
        }
        .metric-label {
            font-size: 1rem;
            text-align: center;
            color: #666;
        }

        /* Rodapé com visual mais leve e separado do conteúdo */
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 1rem;
            background-color: #f5f0e1;
            border-radius: 10px;
        }
        
        /* Personalização dos botões padrão do Streamlit */
        .stButton>button {
            background-color: #1e3d59;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #2b5d8b;
        }
        
        /* Selectbox customizado */
        .stSelectbox {
            background-color: white;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        
        /* Slider customizado, com mais espaçamento */
        .stSlider {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        
        /* Container customizado para gráficos (Plotly etc) */
        .plot-container {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Aba personalizadas (se você usar st.tabs) */
        .stTab {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        
        /* Melhorando aparência das tabelas/dataframes do Streamlit */
        .dataframe {
            border: none !important;
            border-collapse: collapse !important;
        }
        .dataframe th {
            background-color: #1e3d59 !important;
            color: white !important;
            padding: 12px !important;
        }
        .dataframe td {
            padding: 10px !important;
            border: 1px solid #ddd !important;
        }
        
        /* Bordas e sombreamento para gráficos do Plotly */
        .js-plotly-plot {
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Spinner (carregando) customizado */
        .stSpinner {
            text-align: center;
            color: #1e3d59;
        }

        /* Avisos ou mensagens de alerta do Streamlit estilizados */
        .stAlert {
            background-color: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            border-left: 5px solid #ffeeba;
        }

        /* Aparência para área de upload de arquivo */
        .uploadedFile {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border: 1px dashed #dee2e6;
        }

        /* Classe para centralizar gráficos principais */
        .centered-graph {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px auto;
            width: 70%;
        }

        /* Container padronizado para blocos de gráfico */
        .graph-container {
            margin: 20px 0;
            padding: 15px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* Layout grid para painéis analíticos */
        .analysis-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }

        /* Tabela de comparação */
        .comparison-table {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        /* Radar chart container */
        .radar-chart {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        /* Centralizar gráficos de pizza */
        .pie-chart-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }

        /* Dois gráficos lado a lado */
        .two-charts-container {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
            gap: 20px;
        }
        .chart-box {
            flex: 1;
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
    </style>
    """

def apply_custom_css():
    st.markdown(load_css(), unsafe_allow_html=True)