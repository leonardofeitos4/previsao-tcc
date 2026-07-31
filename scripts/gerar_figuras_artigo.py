# -*- coding: utf-8 -*-
"""Gera as figuras do artigo (tex/tcc_artigo/figuras) a partir dos modelos salvos.

Reproduz exatamente o pipeline do notebooks/06_comparacao_modelos.ipynb:
mesmas 15 features, mesma separação temporal (treino 2014-2022, teste 2023-2024),
mesma imputação por mediana do treino e mesmo StandardScaler.

Figuras geradas (PNG, 200 dpi):
  - roc_comparacao_4modelos.png       Curvas ROC dos 4 modelos no teste
  - comparacao_metricas_4modelos.png  Barras de Acurácia e AUC-ROC por modelo
  - matrizes_confusao_4modelos.png    Matrizes de confusão dos 4 modelos
  - walkforward_auc_folds.png         AUC-ROC por fold do walk-forward
"""
import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, roc_auc_score, roc_curve, auc,
                             confusion_matrix)

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DIR_FIGS = [os.path.join(RAIZ, 'resultados', 'figuras'),
            os.path.join(RAIZ, 'tex', 'tcc_artigo', 'figuras')]

TARGET = 'Status_bin'
METRICAS = ['Pts', 'SG', 'Gols_Pro', 'Gols_Contra', 'V', 'Aproveitamento']
JANELAS = [3, 5]
FEATURES_ELENCO = ['Plantel', 'Estrangeiros', 'Valor de Mercado Total']
FEATURES_JANELA = [f'{m}_media_{w}' for m in METRICAS for w in JANELAS]
FEATURES = FEATURES_ELENCO + FEATURES_JANELA

CORES = {'Regressao Logistica': '#1e3d59', 'Random Forest': '#2e7d32',
         'XGBoost': '#e53935', 'LightGBM': '#f57c00'}
ROTULOS = {'Regressao Logistica': 'Regressão Logística'}


def salvar(fig, nome):
    for d in DIR_FIGS:
        os.makedirs(d, exist_ok=True)
        fig.savefig(os.path.join(d, nome), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'✓ {nome}')


# ── Reconstrução da base (idêntica ao notebook 06) ───────────────────────────
df = pd.read_excel(os.path.join(RAIZ, 'dados', 'processados', 'BASE_FINAL.xlsx'),
                   sheet_name='CLUBES')
df.columns = df.columns.str.strip()
df[TARGET] = df['Situacao'].apply(lambda x: 1 if str(x).strip().lower() == 'rebaixado' else 0)

df_desemp = pd.read_excel(os.path.join(RAIZ, 'dados', 'brutos',
                                       'tabela_desempenho_brasileirao.xlsx'),
                          sheet_name='Todos')
df_desemp.columns = df_desemp.columns.str.strip()
df_desemp = df_desemp.sort_values(['Clube', 'Temporada']).reset_index(drop=True)
for m in METRICAS:
    for w in JANELAS:
        df_desemp[f'{m}_media_{w}'] = (
            df_desemp.groupby('Clube')[m]
            .transform(lambda x: x.shift(1).rolling(window=w, min_periods=1).mean())
        )

COLS_MERGE = ['Clube', 'Temporada'] + FEATURES_JANELA
clubes_2025 = df['Clube'][df['Temporada'] == 2025].unique()
rows_2025 = []
for clube in clubes_2025:
    hist = df_desemp[df_desemp['Clube'] == clube].sort_values('Temporada', ascending=False)
    row = {'Clube': clube, 'Temporada': 2025}
    for m in METRICAS:
        for w in JANELAS:
            ultimos = hist.head(w)[m]
            row[f'{m}_media_{w}'] = ultimos.mean() if len(ultimos) > 0 else None
    rows_2025.append(row)
df_ext = pd.concat([df_desemp[COLS_MERGE], pd.DataFrame(rows_2025)[COLS_MERGE]],
                   ignore_index=True)
df = df.merge(df_ext[COLS_MERGE], on=['Clube', 'Temporada'], how='left')

df_rot = df[df['Temporada'] < 2025].copy()
df_tr = df_rot[df_rot['Temporada'] <= 2022].copy()
df_te = df_rot[df_rot['Temporada'] > 2022].copy()
mediana_treino = df_tr[FEATURES_JANELA].median()
for col in FEATURES_JANELA:
    df_tr[col] = df_tr[col].fillna(mediana_treino[col])
    df_te[col] = df_te[col].fillna(mediana_treino[col])
scaler = StandardScaler()
X_tr = scaler.fit_transform(df_tr[FEATURES]); y_tr = df_tr[TARGET].values
X_te = scaler.transform(df_te[FEATURES]);     y_te = df_te[TARGET].values
print(f'Treino: {X_tr.shape} | Teste: {X_te.shape}')

# ── Carrega os 4 modelos otimizados salvos pelo notebook 06 ──────────────────
ARQUIVOS = {'Regressao Logistica': 'regressao_logistica.pkl',
            'Random Forest': 'random_forest.pkl',
            'XGBoost': 'xgboost.pkl',
            'LightGBM': 'lightgbm.pkl'}
melhores = {nome: joblib.load(os.path.join(RAIZ, 'modelos', f))
            for nome, f in ARQUIVOS.items()}

resultados = {}
for nome, clf in melhores.items():
    y_pred = clf.predict(X_te)
    y_prob = clf.predict_proba(X_te)[:, 1]
    resultados[nome] = {'acc': accuracy_score(y_te, y_pred),
                        'auc': roc_auc_score(y_te, y_prob),
                        'y_pred': y_pred, 'y_prob': y_prob}
    print(f"{nome:<22} Acurácia={resultados[nome]['acc']:.3f}  "
          f"AUC-ROC={resultados[nome]['auc']:.3f}")

# ── Figura 1: Curvas ROC ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
for nome, res in resultados.items():
    fpr, tpr, _ = roc_curve(y_te, res['y_prob'])
    ax.plot(fpr, tpr, lw=2, color=CORES[nome],
            label=f"{ROTULOS.get(nome, nome)} (AUC = {auc(fpr, tpr):.3f})")
ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Classificador aleatório')
ax.set_xlabel('Taxa de Falsos Positivos')
ax.set_ylabel('Taxa de Verdadeiros Positivos')
ax.legend(loc='lower right'); ax.grid(alpha=0.3)
salvar(fig, 'roc_comparacao_4modelos.png')

# ── Figura 2: Comparação de métricas ─────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
nomes = list(resultados)
rotulos = [ROTULOS.get(n, n) for n in nomes]
for ax, met, titulo in zip(axes, ['acc', 'auc'], ['Acurácia', 'AUC-ROC']):
    vals = [resultados[n][met] for n in nomes]
    barras = ax.bar(rotulos, vals, color=[CORES[n] for n in nomes], width=0.6)
    ax.set_title(titulo); ax.set_ylim(0, 1.0); ax.grid(alpha=0.3, axis='y')
    ax.bar_label(barras, fmt='%.3f', padding=2)
    ax.tick_params(axis='x', rotation=20)
salvar(fig, 'comparacao_metricas_4modelos.png')

# ── Figura 3: Matrizes de confusão ───────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(18, 4.2))
for ax, (nome, res) in zip(axes, resultados.items()):
    cm = confusion_matrix(y_te, res['y_pred'], labels=[1, 0])
    ax.imshow(cm, cmap='Blues')
    for (i, j), v in np.ndenumerate(cm):
        cor = 'white' if v > cm.max() / 2 else '#1e3d59'
        ax.text(j, i, str(v), ha='center', va='center', fontsize=14, color=cor)
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(['Rebaixado', 'Permaneceu'])
    ax.set_yticklabels(['Rebaixado', 'Permaneceu'])
    ax.set_xlabel('Classe prevista'); ax.set_ylabel('Classe real')
    ax.set_title(f"{ROTULOS.get(nome, nome)}\nAcurácia: {res['acc']:.1%}")
fig.tight_layout()
salvar(fig, 'matrizes_confusao_4modelos.png')

# ── Figura 4: Walk-forward (retreina modelos base por fold, como no nb 06) ──
MODELOS_BASE = {
    'Regressao Logistica': LogisticRegression(C=1.0, random_state=42, max_iter=1000,
                                              class_weight='balanced'),
    'Random Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced',
                                            random_state=42),
    'XGBoost': XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss',
                             scale_pos_weight=4, verbosity=0),
    'LightGBM': LGBMClassifier(n_estimators=100, random_state=42,
                               class_weight='balanced', verbose=-1),
}
temporadas_treino = sorted(df_tr['Temporada'].unique())
N_FOLDS = 5; inicio_val = len(temporadas_treino) - N_FOLDS
wf_results = {nome: [] for nome in MODELOS_BASE}
anos_val = []
for i in range(N_FOLDS):
    anos_tr = temporadas_treino[:inicio_val + i]
    ano_val = temporadas_treino[inicio_val + i]
    anos_val.append(ano_val)
    d_tr = df_rot[df_rot['Temporada'].isin(anos_tr)].copy()
    d_val = df_rot[df_rot['Temporada'] == ano_val].copy()
    med = d_tr[FEATURES_JANELA].median()
    for col in FEATURES_JANELA:
        d_tr[col] = d_tr[col].fillna(med[col])
        d_val[col] = d_val[col].fillna(med[col])
    sc = StandardScaler()
    Xf = sc.fit_transform(d_tr[FEATURES]); Xv = sc.transform(d_val[FEATURES])
    yf = d_tr[TARGET].values;              yv = d_val[TARGET].values
    for nome, clf in MODELOS_BASE.items():
        clf.fit(Xf, yf)
        wf_results[nome].append(roc_auc_score(yv, clf.predict_proba(Xv)[:, 1]))

print('\nWalk-forward — AUC médio por modelo:')
for nome, aucs in wf_results.items():
    print(f'  {nome:<22} {np.nanmean(aucs):.3f} (± {np.nanstd(aucs):.3f})')

fig, ax = plt.subplots(figsize=(9, 5))
for nome, aucs in wf_results.items():
    ax.plot(range(1, N_FOLDS + 1), aucs, marker='o', lw=2, color=CORES[nome],
            label=ROTULOS.get(nome, nome))
ax.set_xlabel('Fold (temporada de validação)')
ax.set_ylabel('AUC-ROC')
ax.set_xticks(range(1, N_FOLDS + 1))
ax.set_xticklabels([str(a) for a in anos_val])
ax.legend(); ax.grid(alpha=0.3)
salvar(fig, 'walkforward_auc_folds.png')

print('\nConcluído.')
