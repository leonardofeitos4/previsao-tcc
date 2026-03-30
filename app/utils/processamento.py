"""
utils/processamento.py
----------------------
Módulo central de processamento de dados e modelos para o TCC de Previsão de
Rebaixamento no Brasileirão Série A.

Responsabilidades:
- Carregar e pré-processar os dados históricos (CSV e Excel)
- Separar conjuntos de treino / teste / previsão por período temporal
- Treinar e salvar o modelo de Regressão Logística + StandardScaler
- Avaliar métricas do modelo no conjunto de teste
- Realizar previsões para novos dados

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
FEATURES = ['Plantel', 'Estrangeiros', 'Valor de Mercado Total']
TARGET   = 'Status_bin'

ANO_CORTE_TREINO = 2022   # inclusive
ANO_PREVISAO     = 2025

MODELO_PATH = os.path.join("modelos", "modelo_logit_status.pkl")
SCALER_PATH = os.path.join("modelos", "scaler_logit_status.pkl")


# ─────────────────────────────────────────────
# CARREGAMENTO DE DADOS
# ─────────────────────────────────────────────

@st.cache_data
def carregar_dados() -> pd.DataFrame:
    """
    Lê dados/BASE_FINAL.csv e cria a coluna Status_bin.

    Status_bin:
        0 → rebaixado  (Situacao == 'Rebaixado')
        1 → permaneceu (qualquer outro valor)

    Returns:
        pd.DataFrame com Status_bin incluído.
    """
    caminho = os.path.join("dados", "BASE_FINAL.csv")
    df = pd.read_csv(caminho)
    df.columns = df.columns.str.strip()
    df = _criar_status_bin(df)
    return df


@st.cache_data
def carregar_dados_excel() -> pd.DataFrame:
    """
    Lê dados/BASE_FINAL.xlsx (aba CLUBES) e cria a coluna Status_bin.

    Returns:
        pd.DataFrame com Status_bin incluído.
    """
    caminho = os.path.join("dados", "BASE_FINAL.xlsx")
    try:
        df = pd.read_excel(caminho, sheet_name="CLUBES")
    except Exception:
        # Fallback: primeira aba disponível
        df = pd.read_excel(caminho)
    df.columns = df.columns.str.strip()
    df = _criar_status_bin(df)
    return df


def _criar_status_bin(df: pd.DataFrame) -> pd.DataFrame:
    """Cria a coluna Status_bin a partir de Situacao ou Status."""
    if 'Situacao' in df.columns:
        df[TARGET] = df['Situacao'].apply(
            lambda x: 0 if str(x).strip().lower() == 'rebaixado' else 1
        )
    elif 'Status' in df.columns:
        # Status numérico: assume 3 = Rebaixado
        df[TARGET] = df['Status'].apply(
            lambda x: 0 if pd.notna(x) and int(x) == 3 else 1
        )
    else:
        raise ValueError("A base de dados não possui coluna 'Situacao' nem 'Status'.")
    return df


# ─────────────────────────────────────────────
# SEPARAÇÃO DE CONJUNTOS (por período temporal)
# ─────────────────────────────────────────────

def separar_conjuntos(df: pd.DataFrame):
    """
    Separa o DataFrame em treino, teste e previsão por período temporal.
    NUNCA usa separação aleatória (dados de série temporal).

    Treino  : Temporada <= ANO_CORTE_TREINO  (2014 – 2022)
    Teste   : 2023 <= Temporada < ANO_PREVISAO (2023 – 2024)
    Previsão: Temporada == ANO_PREVISAO       (2025)

    Args:
        df: DataFrame completo com coluna 'Temporada'.

    Returns:
        tuple(df_treino, df_teste, df_prev)
    """
    df_treino = df[df['Temporada'] <= ANO_CORTE_TREINO].copy()
    df_teste  = df[(df['Temporada'] > ANO_CORTE_TREINO) &
                   (df['Temporada'] < ANO_PREVISAO)].copy()
    df_prev   = df[df['Temporada'] == ANO_PREVISAO].copy()
    return df_treino, df_teste, df_prev


# ─────────────────────────────────────────────
# TREINAMENTO
# ─────────────────────────────────────────────

def treinar_modelo(df_treino: pd.DataFrame):
    """
    Treina Regressão Logística com StandardScaler ajustado APENAS no treino.

    Args:
        df_treino: DataFrame de treino com colunas FEATURES e TARGET.

    Returns:
        tuple(modelo, scaler)
    """
    X_treino = df_treino[FEATURES]
    y_treino = df_treino[TARGET]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_treino)

    modelo = LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')
    modelo.fit(X_scaled, y_treino)

    return modelo, scaler


# ─────────────────────────────────────────────
# PERSISTÊNCIA
# ─────────────────────────────────────────────

def salvar_modelo(modelo, scaler) -> None:
    """Salva modelo e scaler em modelos/."""
    os.makedirs("modelos", exist_ok=True)
    joblib.dump(modelo, MODELO_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"Modelo salvo em: {MODELO_PATH}")
    print(f"Scaler salvo em: {SCALER_PATH}")


@st.cache_resource
def carregar_modelo():
    """
    Carrega modelo e scaler salvos em disco.

    Returns:
        tuple(modelo, scaler)
    """
    modelo = joblib.load(MODELO_PATH)
    scaler = joblib.load(SCALER_PATH)
    return modelo, scaler


# ─────────────────────────────────────────────
# AVALIAÇÃO
# ─────────────────────────────────────────────

def avaliar_modelo(modelo, scaler, df_teste: pd.DataFrame) -> dict:
    """
    Avalia o modelo no conjunto de teste.

    Args:
        modelo: Modelo treinado.
        scaler: Scaler ajustado no treino.
        df_teste: DataFrame de teste com FEATURES e TARGET.

    Returns:
        dict com keys: acuracia, mae, rmse, relatorio
    """
    X_teste = scaler.transform(df_teste[FEATURES])
    y_teste = df_teste[TARGET]

    y_pred = modelo.predict(X_teste)

    acuracia = accuracy_score(y_teste, y_pred)
    mae      = mean_absolute_error(y_teste, y_pred)
    rmse     = np.sqrt(mean_squared_error(y_teste, y_pred))
    relatorio = classification_report(y_teste, y_pred,
                                      target_names=['Rebaixado', 'Permaneceu'])

    return {
        'acuracia':  acuracia,
        'mae':       mae,
        'rmse':      rmse,
        'relatorio': relatorio
    }


# ─────────────────────────────────────────────
# PREVISÃO
# ─────────────────────────────────────────────

def fazer_previsao(dados_entrada_df: pd.DataFrame):
    """
    Realiza previsão para novos dados usando o modelo salvo.

    Args:
        dados_entrada_df: DataFrame com as 3 colunas de FEATURES.

    Returns:
        tuple(previsao, probabilidades)
            previsao      : array de int (0 = Rebaixado, 1 = Permaneceu)
            probabilidades: array shape (n, 2)
                            probabilidades[:, 0] → prob. de rebaixamento
                            probabilidades[:, 1] → prob. de permanência
    """
    modelo, scaler = carregar_modelo()

    dados_filtrados = dados_entrada_df[FEATURES]
    dados_scaled    = scaler.transform(dados_filtrados)

    previsao      = modelo.predict(dados_scaled)
    probabilidade = modelo.predict_proba(dados_scaled)

    # Garantir orientação correta: classe 0 = Rebaixado
    # O LogisticRegression ordena classes em ordem crescente.
    # classes_[0] deve ser 0 (Rebaixado).
    if modelo.classes_[0] == 1:
        # Se a classe 0 do modelo for "1" (permanência), inverte
        previsao      = 1 - previsao
        probabilidade = np.column_stack((probabilidade[:, 1], probabilidade[:, 0]))

    return previsao, probabilidade
