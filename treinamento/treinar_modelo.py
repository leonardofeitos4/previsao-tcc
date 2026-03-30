"""
treinar_modelo.py
-----------------
Script standalone para treinamento, avaliacao e salvamento do modelo de
Previsao de Rebaixamento no Brasileirao Serie A.

Fluxo:
  1. Carrega dados/BASE_FINAL.xlsx (aba CLUBES)
  2. Cria Status_bin  (0 = rebaixado | 1 = permaneceu)
  3. Separa treino (2014-2022) e teste (2023-2024) por periodo temporal
  4. Ajusta StandardScaler APENAS no conjunto de treino
  5. Treina 3 modelos: Regressao Logistica, Random Forest, SVM
  6. Avalia os 3 modelos no teste e exibe tabela de metricas
  7. Exibe classification_report da Regressao Logistica
  8. Salva matrizes de confusao em img/matrizes_confusao.png
  9. Retreina Regressao Logistica com TODOS os dados rotulados (2014-2024)
 10. Salva modelo e scaler em modelos/
 11. Exibe coeficientes do modelo final

Autor: Leonardo Feitosa - Ciencia de Dados / UFPB
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # backend nao interativo para salvar figuras
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, mean_absolute_error, mean_squared_error,
    classification_report, confusion_matrix
)

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
FEATURES         = ['Plantel', 'Estrangeiros', 'Valor de Mercado Total']
TARGET           = 'Status_bin'
ANO_CORTE_TREINO = 2022
ANO_PREVISAO     = 2025
ARQUIVO_DADOS    = os.path.join("dados", "BASE_FINAL.xlsx")
MODELO_PATH      = os.path.join("modelos", "modelo_logit_status.pkl")
SCALER_PATH      = os.path.join("modelos", "scaler_logit_status.pkl")
IMG_PATH         = os.path.join("img", "matrizes_confusao.png")


# ─────────────────────────────────────────────
# 1. CARREGAMENTO DOS DADOS
# ─────────────────────────────────────────────
print("=" * 60)
print("  TREINAMENTO - Previsao de Rebaixamento Serie A")
print("=" * 60)
print(f"\n[1] Carregando {ARQUIVO_DADOS} ...")

try:
    df = pd.read_excel(ARQUIVO_DADOS, sheet_name="CLUBES")
except Exception:
    df = pd.read_excel(ARQUIVO_DADOS)

df.columns = df.columns.str.strip()
print(f"    Registros carregados: {len(df)}")
print(f"    Temporadas: {sorted(df['Temporada'].unique())}")


# ─────────────────────────────────────────────
# 2. CRIACAO DE Status_bin
# ─────────────────────────────────────────────
print("\n[2] Criando variavel dependente Status_bin ...")

if 'Situacao' in df.columns:
    df[TARGET] = df['Situacao'].apply(
        lambda x: 0 if str(x).strip().lower() == 'rebaixado' else 1
    )
elif 'Status' in df.columns:
    df[TARGET] = df['Status'].apply(
        lambda x: 0 if pd.notna(x) and int(x) == 3 else 1
    )
else:
    print("ERRO: Coluna 'Situacao' ou 'Status' nao encontrada.")
    sys.exit(1)

print(f"    Distribuicao Status_bin:")
print(f"      0 (Rebaixado) : {(df[TARGET]==0).sum()}")
print(f"      1 (Permaneceu): {(df[TARGET]==1).sum()}")


# ─────────────────────────────────────────────
# 3. SEPARACAO POR PERIODO TEMPORAL
# ─────────────────────────────────────────────
print(f"\n[3] Separando conjuntos por periodo temporal ...")

df_rotulado = df[df['Temporada'] < ANO_PREVISAO].copy()
df_treino   = df_rotulado[df_rotulado['Temporada'] <= ANO_CORTE_TREINO].copy()
df_teste    = df_rotulado[df_rotulado['Temporada']  > ANO_CORTE_TREINO].copy()

print(f"    Treino (2014-{ANO_CORTE_TREINO}): {len(df_treino)} registros")
print(f"    Teste  ({ANO_CORTE_TREINO+1}-{ANO_PREVISAO-1}): {len(df_teste)} registros")

X_treino = df_treino[FEATURES]
y_treino = df_treino[TARGET]
X_teste  = df_teste[FEATURES]
y_teste  = df_teste[TARGET]


# ─────────────────────────────────────────────
# 4. SCALER - ajustado APENAS no treino
# ─────────────────────────────────────────────
print("\n[4] Ajustando StandardScaler no conjunto de treino ...")

scaler      = StandardScaler()
X_treino_sc = scaler.fit_transform(X_treino)
X_teste_sc  = scaler.transform(X_teste)

print("    Medias  (treino):", {k: round(v, 2) for k, v in zip(FEATURES, scaler.mean_)})
print("    Desvios (treino):", {k: round(v, 2) for k, v in zip(FEATURES, scaler.scale_)})


# ─────────────────────────────────────────────
# 5. TREINAMENTO DOS 3 MODELOS
# ─────────────────────────────────────────────
print("\n[5] Treinando 3 modelos ...")

modelos = {
    'Regressao Logistica': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
    'Random Forest':       RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
    'SVM':                 SVC(probability=True, random_state=42, class_weight='balanced')
}

modelos_treinados = {}
for nome, m in modelos.items():
    m.fit(X_treino_sc, y_treino)
    modelos_treinados[nome] = m
    print(f"    OK: {nome} treinado.")


# ─────────────────────────────────────────────
# 6. AVALIACAO NO CONJUNTO DE TESTE
# ─────────────────────────────────────────────
print("\n[6] Avaliando modelos no conjunto de teste ...")
print()

resultados = []
for nome, m in modelos_treinados.items():
    y_pred = m.predict(X_teste_sc)
    acc    = accuracy_score(y_teste, y_pred)
    mae    = mean_absolute_error(y_teste, y_pred)
    rmse   = float(np.sqrt(mean_squared_error(y_teste, y_pred)))
    resultados.append({'Modelo': nome, 'Acuracia': acc, 'MAE': mae, 'RMSE': rmse})

print("  +---------------------------+----------+--------+--------+")
print("  | Modelo                    | Acuracia |   MAE  |  RMSE  |")
print("  +---------------------------+----------+--------+--------+")
for r in resultados:
    print(f"  | {r['Modelo']:<25} | {r['Acuracia']:.4f}   | {r['MAE']:.4f} | {r['RMSE']:.4f} |")
print("  +---------------------------+----------+--------+--------+")


# ─────────────────────────────────────────────
# 7. CLASSIFICATION REPORT - Regressao Logistica
# ─────────────────────────────────────────────
print("\n[7] Classification Report - Regressao Logistica:")
y_pred_logit = modelos_treinados['Regressao Logistica'].predict(X_teste_sc)
print(classification_report(
    y_teste, y_pred_logit,
    target_names=['Rebaixado (0)', 'Permaneceu (1)']
))


# ─────────────────────────────────────────────
# 8. MATRIZES DE CONFUSAO
# ─────────────────────────────────────────────
print("[8] Salvando matrizes de confusao ...")

os.makedirs("img", exist_ok=True)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Matrizes de Confusao - Conjunto de Teste (2023-2024)", fontsize=14)

for ax, (nome, m) in zip(axes, modelos_treinados.items()):
    y_pred = m.predict(X_teste_sc)
    cm     = confusion_matrix(y_teste, y_pred)
    sns.heatmap(
        cm, annot=True, fmt='d', ax=ax,
        cmap='Blues',
        xticklabels=['Rebaixado', 'Permaneceu'],
        yticklabels=['Rebaixado', 'Permaneceu']
    )
    ax.set_title(nome)
    ax.set_xlabel('Previsto')
    ax.set_ylabel('Real')

plt.tight_layout()
plt.savefig(IMG_PATH, dpi=150, bbox_inches='tight')
plt.close()
print(f"    Salvas em: {IMG_PATH}")


# ─────────────────────────────────────────────
# 9. RETREINAMENTO COM TODOS OS DADOS ROTULADOS
# ─────────────────────────────────────────────
print("\n[9] Retreinando Regressao Logistica com todos os dados (2014-2024) ...")

X_todos = df_rotulado[FEATURES]
y_todos = df_rotulado[TARGET]

scaler_final = StandardScaler()
X_todos_sc   = scaler_final.fit_transform(X_todos)

modelo_final = LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')
modelo_final.fit(X_todos_sc, y_todos)
print(f"    Registros utilizados: {len(df_rotulado)}")


# ─────────────────────────────────────────────
# 10. SALVAR MODELO E SCALER
# ─────────────────────────────────────────────
print("\n[10] Salvando modelo final e scaler ...")
os.makedirs("modelos", exist_ok=True)
joblib.dump(modelo_final, MODELO_PATH)
joblib.dump(scaler_final, SCALER_PATH)
print(f"    Modelo salvo: {MODELO_PATH}")
print(f"    Scaler salvo: {SCALER_PATH}")


# ─────────────────────────────────────────────
# 11. COEFICIENTES DO MODELO FINAL
# ─────────────────────────────────────────────
print("\n[11] Coeficientes do modelo final (Regressao Logistica):")
coef_df = pd.DataFrame({
    'Feature':     FEATURES,
    'Coeficiente': modelo_final.coef_[0].round(4)
}).sort_values('Coeficiente', ascending=False)
print(coef_df.to_string(index=False))
print(f"\n    Intercepto: {modelo_final.intercept_[0]:.4f}")
print("\n    Interpretacao:")
print("    > Coef. positivo -> aumenta prob. de permanencia (classe 1)")
print("    > Coef. negativo -> aumenta prob. de rebaixamento (classe 0)")

print("\n" + "=" * 60)
print("  Treinamento concluido! Execute: streamlit run app.py")
print("=" * 60)
