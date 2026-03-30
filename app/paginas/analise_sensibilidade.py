import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from app.utils.processamento import fazer_previsao

def main():
    
    # Título da seção de análise de sensibilidade
    st.markdown("<h3 class='subheader'>Análise de Sensibilidade</h3>", unsafe_allow_html=True)
    
    # Descrição da seção
    st.markdown("""
    <div class="card">
        <p>Esta seção permite explorar como cada variável afeta a probabilidade de rebaixamento. 
        Ajuste os controles deslizantes para ver como o risco muda quando você altera um fator mantendo os outros constantes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Valores base para análise de sensibilidade
    base_plantel = 25
    base_estrangeiros = 3
    base_valor = 50.0
    
    # Divisão da tela em 3 colunas
    col1, col2, col3 = st.columns(3)
    
    # Análise de impacto do Tamanho do Elenco
    with col1:
        st.markdown("<h4>Tamanho do Elenco</h4>", unsafe_allow_html=True)
        plantel_range = list(range(15, 51, 5))  # Intervalo de tamanhos de elenco
        resultados_plantel = []
        
        # Loop para calcular a probabilidade de rebaixamento para diferentes tamanhos de elenco
        for p in plantel_range:
            dados = pd.DataFrame({
                'Plantel': [p],
                'Estrangeiros': [base_estrangeiros],
                'Valor de Mercado Total': [base_valor]
            })
            _, prob = fazer_previsao(dados)  # Previsão da probabilidade de rebaixamento
            resultados_plantel.append(prob[0][1])
        
        # Criação do DataFrame com os resultados para o gráfico
        df_plantel = pd.DataFrame({
            'Tamanho do Elenco': plantel_range,
            'Probabilidade de Rebaixamento': resultados_plantel
        })
        
        # Gráfico de linha para mostrar o impacto do Tamanho do Elenco
        fig_plantel = px.line(df_plantel, x='Tamanho do Elenco', y='Probabilidade de Rebaixamento',
                           markers=True, title="Impacto do Tamanho do Elenco")
        fig_plantel.update_layout(yaxis_tickformat='.0%')  # Formatação do eixo y
        st.plotly_chart(fig_plantel, use_container_width=True)
    
    # Análise de impacto do Número de Estrangeiros
    with col2:
        st.markdown("<h4>Número de Estrangeiros</h4>", unsafe_allow_html=True)
        estrangeiros_range = list(range(0, 16, 2))  # Intervalo para o número de estrangeiros
        resultados_estrangeiros = []
        
        # Loop para calcular a probabilidade de rebaixamento para diferentes números de estrangeiros
        for e in estrangeiros_range:
            dados = pd.DataFrame({
                'Plantel': [base_plantel],
                'Estrangeiros': [e],
                'Valor de Mercado Total': [base_valor]
            })
            _, prob = fazer_previsao(dados)
            resultados_estrangeiros.append(prob[0][1])
        
        # Criação do DataFrame com os resultados para o gráfico
        df_estrangeiros = pd.DataFrame({
            'Número de Estrangeiros': estrangeiros_range,
            'Probabilidade de Rebaixamento': resultados_estrangeiros
        })
        
        # Gráfico de linha para mostrar o impacto do Número de Estrangeiros
        fig_estrangeiros = px.line(df_estrangeiros, x='Número de Estrangeiros', y='Probabilidade de Rebaixamento',
                                markers=True, title="Impacto do Número de Estrangeiros")
        fig_estrangeiros.update_layout(yaxis_tickformat='.0%')  # Formatação do eixo y
        st.plotly_chart(fig_estrangeiros, use_container_width=True)
    
    # Análise de impacto do Valor de Mercado
    with col3:
        st.markdown("<h4>Valor de Mercado</h4>", unsafe_allow_html=True)
        valor_range = list(range(10, 301, 30))  # Intervalo de valores de mercado
        resultados_valor = []
        
        # Loop para calcular a probabilidade de rebaixamento para diferentes valores de mercado
        for v in valor_range:
            dados = pd.DataFrame({
                'Plantel': [base_plantel],
                'Estrangeiros': [base_estrangeiros],
                'Valor de Mercado Total': [v]
            })
            _, prob = fazer_previsao(dados)
            resultados_valor.append(prob[0][1])
        
        # Criação do DataFrame com os resultados para o gráfico
        df_valor = pd.DataFrame({
            'Valor de Mercado (M€)': valor_range,
            'Probabilidade de Rebaixamento': resultados_valor
        })
        
        # Gráfico de linha para mostrar o impacto do Valor de Mercado
        fig_valor = px.line(df_valor, x='Valor de Mercado (M€)', y='Probabilidade de Rebaixamento',
                         markers=True, title="Impacto do Valor de Mercado")
        fig_valor.update_layout(yaxis_tickformat='.0%')  # Formatação do eixo y
        st.plotly_chart(fig_valor, use_container_width=True)

    # Gráfico 3D para visualizar a interação entre as variáveis
    st.markdown("<h3 class='subheader'>Interação entre Variáveis</h3>", unsafe_allow_html=True)
    
    # Definindo os valores para análise 3D
    plantel_3d = [20, 25, 30, 35, 40]
    valor_3d = [20, 50, 100, 150, 200]
    
    # Criação do DataFrame para armazenar os resultados da análise 3D
    df_3d = pd.DataFrame(columns=['Plantel', 'Valor de Mercado (M€)', 'Probabilidade de Rebaixamento'])
    
    # Loop para calcular a probabilidade de rebaixamento para diferentes combinações de Plantel e Valor de Mercado
    for p in plantel_3d:
        for v in valor_3d:
            dados = pd.DataFrame({
                'Plantel': [p],
                'Estrangeiros': [base_estrangeiros],
                'Valor de Mercado Total': [v]
            })
            _, prob = fazer_previsao(dados)
            df_3d = pd.concat([df_3d, pd.DataFrame({
                'Plantel': [p],
                'Valor de Mercado (M€)': [v],
                'Probabilidade de Rebaixamento': [prob[0][1]]
            })], ignore_index=True)
    
    # Gráfico 3D para mostrar a interação entre Plantel, Valor de Mercado e Probabilidade de Rebaixamento
    fig_3d = px.scatter_3d(df_3d, x='Plantel', y='Valor de Mercado (M€)', z='Probabilidade de Rebaixamento',
                        color='Probabilidade de Rebaixamento', opacity=0.7,
                        color_continuous_scale=px.colors.sequential.Viridis)
    
    fig_3d.update_layout(height=600, scene=dict(
        zaxis=dict(tickformat='.0%')
    ))  # Formatação do eixo Z
    st.plotly_chart(fig_3d, use_container_width=True)

# Executa o aplicativo Streamlit
if __name__ == "__main__":
    main()
