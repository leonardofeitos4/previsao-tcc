import streamlit as st
import pandas as pd
import plotly.express as px
from app.utils.processamento import carregar_dados

def main():
    st.markdown("<h3 class='subheader'>Base de Dados Histórica</h3>", unsafe_allow_html=True)
    
    df = carregar_dados()
    df_display = df.copy()

    # Corrige valores inválidos na coluna Temporada
    df_display['Temporada'] = df_display['Temporada'].astype(str).str.replace(',', '').str.strip()
    df_display = df_display[df_display['Temporada'] != '']

    # Renomeia colunas para incluir (M€)
    if 'Valor de Mercado Total' in df_display.columns:
        df_display.rename(columns={'Valor de Mercado Total': 'Valor de Mercado Total (M€)'}, inplace=True)
    if 'Valor de Mercado' in df_display.columns:
        df_display.rename(columns={'Valor de Mercado': 'Valor de Mercado (M€)'}, inplace=True)

    # Padroniza 'Situação'
    if 'Situacao' in df_display.columns:
        df_display['Situacao'] = df_display['Situacao'].replace({
            'Top4': 'Top 4',
            'SerieA': 'Série A',
            'SérieA': 'Série A',
            'Serie B para Série A': 'Série B para Série A',
            'SerieB_Para_SerieA': 'Série B para Série A',
            'Rebaixado': 'Rebaixado'
        })
        df_display['Situação'] = df_display['Situacao']
    elif 'Status' in df_display.columns:
        status_mapping = {0: "Top 4", 1: "Série A", 2: "Série B para Série A", 3: "Rebaixado"}
        df_display['Status'] = pd.to_numeric(df_display['Status'], errors='coerce')
        df_display['Situação'] = df_display['Status'].map(lambda x: status_mapping.get(x, x) if pd.notna(x) else "Desconhecido")
    else:
        df_display['Situação'] = "Desconhecido"

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        situacao_options = sorted(df_display['Situação'].dropna().unique())
        situacao_filter = st.multiselect("Situação", options=situacao_options, default=situacao_options)
    
    with col2:
        clubes_options = sorted(df_display['Clube'].dropna().unique())
        default_clubes = ["Flamengo", "Palmeiras"]
        clube_filter = st.multiselect("Clube", options=["Todos"] + clubes_options, default=default_clubes)
    
    with col3:
        temporada_options = sorted(df_display['Temporada'].dropna().unique())
        temporada_filter = st.multiselect("Temporada", options=["Todos"] + temporada_options, default=["Todos"])
    
    with col4:
        min_valor = st.number_input("Valor Mínimo (M€)", value=0.0)

    # Tratamento dos filtros
    situacao_filtrada = situacao_filter or situacao_options
    clubes_filtrados = clubes_options if (not clube_filter or "Todos" in clube_filter) else clube_filter
    temporada_filtrada = temporada_options if (not temporada_filter or "Todos" in temporada_filter) else temporada_filter

    filtered_df = df_display[
        (df_display['Situação'].isin(situacao_filtrada)) &
        (df_display['Clube'].isin(clubes_filtrados)) &
        (df_display['Temporada'].isin(temporada_filtrada)) &
        (df_display['Valor de Mercado Total (M€)'] >= min_valor)
    ]

    st.dataframe(filtered_df, use_container_width=True, height=400)

    col1, col2 = st.columns(2)

    # Gráfico de comparação entre times
    with col1:
        st.markdown("<h4>Comparação de Times</h4>", unsafe_allow_html=True)
        if not filtered_df.empty:
            df_bar = filtered_df[['Clube', 'Pontos', 'Valor de Mercado Total (M€)', 'Plantel']].copy()
            df_bar = df_bar.groupby('Clube')[['Pontos', 'Valor de Mercado Total (M€)', 'Plantel']].mean().reset_index()
            df_bar_melt = df_bar.melt(id_vars='Clube', var_name='Indicador', value_name='Valor')

            fig_comp = px.bar(
                df_bar_melt, x='Clube', y='Valor', color='Indicador',
                barmode='group', text='Valor',
                labels={'Valor': 'Valor'}, title='Comparação Média por Clube'
            )
            fig_comp.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_comp.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("Nenhum dado para exibir o gráfico.")

    # Gráfico de pizza
    with col2:
        st.markdown("<h4>Proporção de Clubes por Situação</h4>", unsafe_allow_html=True)
        if not filtered_df.empty:
            fig_pie = px.pie(
                filtered_df, names='Situação',
                title='Distribuição dos Clubes',
                hole=0.5
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Nenhum dado para exibir o gráfico.")

    # Gráfico de barras por temporada com rótulos
    st.markdown("<h4>Evolução por Temporada</h4>", unsafe_allow_html=True)
    if not filtered_df.empty:
        df_evolucao = filtered_df[['Clube', 'Temporada', 'Pontos', 'Valor de Mercado Total (M€)']].copy()
        df_evolucao = df_evolucao.groupby(['Clube', 'Temporada'])[['Pontos', 'Valor de Mercado Total (M€)']].mean().reset_index()
        df_evolucao = df_evolucao.melt(id_vars=['Clube', 'Temporada'], var_name='Indicador', value_name='Valor')

        fig_evolucao = px.bar(
            df_evolucao,
            x='Temporada', y='Valor', color='Clube',
            barmode='group', facet_col='Indicador', facet_col_wrap=1,
            text='Valor', labels={'Valor': 'Valor', 'Temporada': 'Temporada'},
            title='Pontuação e Valor de Mercado por Temporada'
        )
        fig_evolucao.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_evolucao.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', height=600)
        st.plotly_chart(fig_evolucao, use_container_width=True)
    else:
        st.info("Nenhum dado disponível para o gráfico de evolução.")

if __name__ == "__main__":
    main()
