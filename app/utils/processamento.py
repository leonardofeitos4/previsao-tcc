"""
utils/processamento.py
----------------------
Módulo central de processamento de dados e modelos para o TCC de Previsão de
Rebaixamento no Brasileirão Série A.

Separação temporal:
  Treino  : 2014 – 2022
  Teste   : 2023 – 2024
  Previsão: 2025

Autor: Leonardo Feitosa — Ciência de Dados / UFPB
"""

import os
import pandas as pd
import numpy as np
import joblib
import streamlit as st

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, mean_absolute_error,
    mean_squared_error, classification_report
)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
METRICAS = ['Pts', 'SG', 'Gols_Pro', 'Gols_Contra', 'V', 'Aproveitamento']
JANELAS  = [3, 5]
FEATURES_ELENCO = ['Plantel', 'Estrangeiros', 'Valor de Mercado Total']
FEATURES_JANELA = [f'{m}_media_{w}' for m in METRICAS for w in JANELAS]
FEATURES = FEATURES_ELENCO + FEATURES_JANELA

TARGET           = 'Status_bin'
ANO_CORTE_TREINO = 2022
ANO_PREVISAO     = 2025

MODELO_PATH  = os.path.join("modelos", "logistica.pkl")
SCALER_PATH  = os.path.join("modelos", "scaler_logistica.pkl")
MEDIAN_PATH  = os.path.join("modelos", "mediana_treino.pkl")


# ─────────────────────────────────────────────
# HELPERS INTERNOS
# ─────────────────────────────────────────────

def _criar_status_bin(df: pd.DataFrame) -> pd.DataFrame:
    if 'Situacao' in df.columns:
        df[TARGET] = df['Situacao'].apply(
            lambda x: 1 if str(x).strip().lower() == 'rebaixado' else 0
        )
    else:
        raise ValueError("A base de dados não possui coluna 'Situacao'.")
    return df


def _computar_janelas(df_desemp: pd.DataFrame) -> tuple:
    """Computa rolling window features em df_desemp e retorna (df_desemp_ext, COLS_MERGE)."""
    for metrica in METRICAS:
        for w in JANELAS:
            df_desemp[f'{metrica}_media_{w}'] = (
                df_desemp.groupby('Clube')[metrica]
                .transform(lambda x: x.shift(1).rolling(window=w, min_periods=1).mean())
            )
    COLS_MERGE = ['Clube', 'Temporada'] + FEATURES_JANELA
    return df_desemp, COLS_MERGE


def _extensao_2025(df_base: pd.DataFrame, df_desemp: pd.DataFrame) -> pd.DataFrame:
    """Cria linhas 2025 com janelas calculadas a partir do histórico até 2024."""
    clubes_2025 = df_base['Clube'][df_base['Temporada'] == 2025].unique()
    rows = []
    for clube in clubes_2025:
        hist = df_desemp[df_desemp['Clube'] == clube].sort_values('Temporada', ascending=False)
        row  = {'Clube': clube, 'Temporada': 2025}
        for metrica in METRICAS:
            for w in JANELAS:
                ultimos = hist.head(w)[metrica]
                row[f'{metrica}_media_{w}'] = ultimos.mean() if len(ultimos) > 0 else None
        rows.append(row)
    return pd.DataFrame(rows)


@st.cache_data
def _carregar_desempenho() -> pd.DataFrame:
    caminho = os.path.join("dados", "tabela_desempenho_brasileirao.xlsx")
    df = pd.read_excel(caminho, sheet_name="Todos")
    df.columns = df.columns.str.strip()
    return df.sort_values(['Clube', 'Temporada']).reset_index(drop=True)


@st.cache_data
def carregar_desempenho_com_janelas() -> pd.DataFrame:
    """Retorna tabela de desempenho histórico com as 12 features de janela deslizante calculadas."""
    df, _ = _computar_janelas(_carregar_desempenho())
    return df


# ─────────────────────────────────────────────
# CARREGAMENTO DE DADOS
# ─────────────────────────────────────────────

@st.cache_data
def carregar_dados() -> pd.DataFrame:
    caminho = os.path.join("dados", "BASE_FINAL.csv")
    df = pd.read_csv(caminho)
    df.columns = df.columns.str.strip()
    return _criar_status_bin(df)


@st.cache_data
def carregar_dados_excel() -> pd.DataFrame:
    """Carrega BASE_FINAL.xlsx e anexa as 12 features de janela deslizante."""
    caminho = os.path.join("dados", "BASE_FINAL.xlsx")
    try:
        df = pd.read_excel(caminho, sheet_name="CLUBES")
    except Exception:
        df = pd.read_excel(caminho)
    df.columns = df.columns.str.strip()
    df = _criar_status_bin(df)

    df_desemp = _carregar_desempenho()
    df_desemp, COLS_MERGE = _computar_janelas(df_desemp)
    df_ext_2025 = _extensao_2025(df, df_desemp)
    df_desemp_ext = pd.concat([df_desemp[COLS_MERGE], df_ext_2025[COLS_MERGE]], ignore_index=True)

    df = df.merge(df_desemp_ext[COLS_MERGE], on=['Clube', 'Temporada'], how='left')
    return df


# ─────────────────────────────────────────────
# SEPARAÇÃO DE CONJUNTOS
# ─────────────────────────────────────────────

def separar_conjuntos(df: pd.DataFrame):
    df_treino = df[df['Temporada'] <= ANO_CORTE_TREINO].copy()
    df_teste  = df[(df['Temporada'] > ANO_CORTE_TREINO) &
                   (df['Temporada'] < ANO_PREVISAO)].copy()
    df_prev   = df[df['Temporada'] == ANO_PREVISAO].copy()
    return df_treino, df_teste, df_prev


# ─────────────────────────────────────────────
# TREINAMENTO
# ─────────────────────────────────────────────

def treinar_modelo(df_treino: pd.DataFrame):
    mediana_treino = df_treino[FEATURES_JANELA].median()
    df_tr = df_treino.copy()
    for col in FEATURES_JANELA:
        df_tr[col] = df_tr[col].fillna(mediana_treino[col])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_tr[FEATURES])
    modelo = LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')
    modelo.fit(X_scaled, df_tr[TARGET])
    return modelo, scaler, mediana_treino


# ─────────────────────────────────────────────
# PERSISTÊNCIA
# ─────────────────────────────────────────────

def salvar_modelo(modelo, scaler, mediana_treino=None) -> None:
    os.makedirs("modelos", exist_ok=True)
    joblib.dump(modelo, MODELO_PATH)
    joblib.dump(scaler, SCALER_PATH)
    if mediana_treino is not None:
        joblib.dump(mediana_treino, MEDIAN_PATH)


@st.cache_resource
def carregar_modelo():
    modelo = joblib.load(MODELO_PATH)
    scaler = joblib.load(SCALER_PATH)
    mediana = joblib.load(MEDIAN_PATH) if os.path.exists(MEDIAN_PATH) else None
    return modelo, scaler, mediana


# ─────────────────────────────────────────────
# AVALIAÇÃO
# ─────────────────────────────────────────────

def avaliar_modelo(modelo, scaler, df_teste: pd.DataFrame, mediana_treino=None) -> dict:
    df_te = df_teste.copy()
    if mediana_treino is not None:
        for col in FEATURES_JANELA:
            if col in df_te.columns:
                df_te[col] = df_te[col].fillna(mediana_treino[col])
            else:
                df_te[col] = mediana_treino[col]

    X_teste = scaler.transform(df_te[FEATURES])
    y_teste = df_te[TARGET]
    y_pred  = modelo.predict(X_teste)

    return {
        'acuracia':  accuracy_score(y_teste, y_pred),
        'mae':       mean_absolute_error(y_teste, y_pred),
        'rmse':      np.sqrt(mean_squared_error(y_teste, y_pred)),
        'relatorio': classification_report(y_teste, y_pred,
                                           target_names=['Permaneceu', 'Rebaixado']),
    }


# ─────────────────────────────────────────────
# PREVISÃO
# ─────────────────────────────────────────────

def fazer_previsao(dados_entrada_df: pd.DataFrame):
    """
    Realiza previsão. Aceita DataFrames com 3 ou 15 features.
    Quando apenas as 3 features de elenco são fornecidas, as 12 features de
    janela deslizante são preenchidas com a mediana do conjunto de treino,
    representando um clube de desempenho histórico médio.
    """
    modelo, scaler, mediana_treino = carregar_modelo()

    df_in = dados_entrada_df.copy()
    for col in FEATURES_JANELA:
        if col not in df_in.columns:
            val = mediana_treino[col] if mediana_treino is not None else 0.0
            df_in[col] = val
        elif mediana_treino is not None:
            df_in[col] = df_in[col].fillna(mediana_treino[col])

    dados_scaled = scaler.transform(df_in[FEATURES])
    previsao     = modelo.predict(dados_scaled)
    probabilidade = modelo.predict_proba(dados_scaled)
    return previsao, probabilidade
