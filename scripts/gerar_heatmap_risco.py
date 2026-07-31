# -*- coding: utf-8 -*-
"""Gera o "Mapa de Calor do Risco" longitudinal (sugestão criativa 1 do parecer).

Para cada temporada T de 2016 a 2025, treina a Regressão Logística final
(mesmos hiperparâmetros de logistica.pkl) apenas com temporadas < T —
janela expansiva, mesmo pipeline dos notebooks (imputação por mediana do
treino + StandardScaler do treino) — e registra a probabilidade prevista
de rebaixamento de cada clube participante de T.

Saída: heatmap_risco_longitudinal.png (resultados/figuras e
tex/tcc_artigo/figuras, 300 dpi). Células com borda preta espessa marcam
rebaixamentos efetivos (codificação redundante à cor, legível em P&B).
As temporadas 2014-2015 servem apenas de histórico inicial de treino.
"""
import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import warnings
warnings.filterwarnings('ignore')

from sklearn.base import clone
from sklearn.preprocessing import StandardScaler

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DIR_FIGS = [os.path.join(RAIZ, 'resultados', 'figuras'),
            os.path.join(RAIZ, 'tex', 'tcc_artigo', 'figuras')]

TARGET = 'Status_bin'
METRICAS = ['Pts', 'SG', 'Gols_Pro', 'Gols_Contra', 'V', 'Aproveitamento']
JANELAS = [3, 5]
FEATURES_ELENCO = ['Plantel', 'Estrangeiros', 'Valor de Mercado Total']
FEATURES_JANELA = [f'{m}_media_{w}' for m in METRICAS for w in JANELAS]
FEATURES = FEATURES_ELENCO + FEATURES_JANELA

ACENTOS = {'Atletico Mineiro': 'Atlético Mineiro', 'Ceara': 'Ceará',
           'Gremio': 'Grêmio', 'Sao Paulo': 'São Paulo', 'Vitoria': 'Vitória',
           'America Mineiro': 'América Mineiro', 'Atletico Goianiense': 'Atlético-GO',
           'Avai': 'Avaí', 'Criciuma': 'Criciúma', 'Chapecoense': 'Chapecoense',
           'Cuiaba': 'Cuiabá', 'Goias': 'Goiás', 'Parana': 'Paraná',
           'Sport Recife': 'Sport Recife'}

REBAIXADOS_REAIS_2025 = {'Ceara', 'Fortaleza', 'Juventude', 'Sport Recife'}


def construir_base():
    """Idêntica à de gerar_analises_v3.py (janelas 3/5)."""
    cols_janela = FEATURES_JANELA
    df = pd.read_excel(os.path.join(RAIZ, 'dados', 'processados', 'BASE_FINAL.xlsx'),
                       sheet_name='CLUBES')
    df.columns = df.columns.str.strip()
    df[TARGET] = df['Situacao'].apply(
        lambda x: 1 if str(x).strip().lower() == 'rebaixado' else 0)

    df_desemp = pd.read_excel(os.path.join(RAIZ, 'dados', 'brutos',
                                           'tabela_desempenho_brasileirao.xlsx'),
                              sheet_name='Todos')
    df_desemp.columns = df_desemp.columns.str.strip()
    df_desemp = df_desemp.sort_values(['Clube', 'Temporada']).reset_index(drop=True)
    for m in METRICAS:
        for w in JANELAS:
            df_desemp[f'{m}_media_{w}'] = (
                df_desemp.groupby('Clube')[m]
                .transform(lambda x: x.shift(1).rolling(window=w, min_periods=1).mean()))

    cols_merge = ['Clube', 'Temporada'] + cols_janela
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
    df_ext = pd.concat([df_desemp[cols_merge], pd.DataFrame(rows_2025)[cols_merge]],
                       ignore_index=True)
    return df.merge(df_ext[cols_merge], on=['Clube', 'Temporada'], how='left')


df = construir_base()
modelo_final = joblib.load(os.path.join(RAIZ, 'modelos', 'logistica.pkl'))

TEMPORADAS = list(range(2016, 2026))
registros = []
for T in TEMPORADAS:
    treino = df[(df['Temporada'] < T) & (df['Temporada'] < 2025)].copy()
    alvo = df[df['Temporada'] == T].copy()
    mediana = treino[FEATURES_JANELA].median()
    for col in FEATURES_JANELA:
        treino[col] = treino[col].fillna(mediana[col])
        alvo[col] = alvo[col].fillna(mediana[col])
    sc = StandardScaler().fit(treino[FEATURES])
    m = clone(modelo_final)
    m.fit(sc.transform(treino[FEATURES]), treino[TARGET].values)
    i1 = list(m.classes_).index(1)
    alvo['prob'] = m.predict_proba(sc.transform(alvo[FEATURES]))[:, i1]
    if T == 2025:
        alvo['rebaixado'] = alvo['Clube'].isin(REBAIXADOS_REAIS_2025).astype(int)
    else:
        alvo['rebaixado'] = alvo[TARGET]
    registros.append(alvo[['Clube', 'Temporada', 'prob', 'rebaixado']])
    print(f'{T}: treino n={len(treino)}  clubes previstos={len(alvo)}')

painel = pd.concat(registros, ignore_index=True)
mat_prob = painel.pivot(index='Clube', columns='Temporada', values='prob')
mat_reb = painel.pivot(index='Clube', columns='Temporada', values='rebaixado')

# Ordena clubes por risco médio decrescente (quem mais "flerta" com a queda no topo)
ordem = mat_prob.mean(axis=1).sort_values(ascending=False).index
mat_prob = mat_prob.loc[ordem]
mat_reb = mat_reb.loc[ordem]

n_lin, n_col = mat_prob.shape
fig, ax = plt.subplots(figsize=(10, 0.42 * n_lin + 2))
cmap = plt.cm.Reds
im = ax.imshow(mat_prob.values, cmap=cmap, vmin=0, vmax=1, aspect='auto')

ax.set_xticks(range(n_col))
ax.set_xticklabels(mat_prob.columns, fontsize=9)
ax.set_yticks(range(n_lin))
ax.set_yticklabels([ACENTOS.get(c, c) for c in mat_prob.index], fontsize=8.5)
ax.set_xlabel('Temporada')

for i in range(n_lin):
    for j in range(n_col):
        p = mat_prob.values[i, j]
        if np.isnan(p):
            ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor='#f2f2f2',
                                   edgecolor='white', lw=0.5, zorder=2))
            continue
        ax.text(j, i, f'{100 * p:.0f}', ha='center', va='center', fontsize=7,
                color='white' if p > 0.55 else '#333333', zorder=4)
        if mat_reb.values[i, j] == 1:
            ax.add_patch(Rectangle((j - 0.47, i - 0.47), 0.94, 0.94, fill=False,
                                   edgecolor='black', lw=1.8, zorder=5))

# Grade branca fina entre células (marcas separadas, grade recessiva)
ax.set_xticks(np.arange(-0.5, n_col, 1), minor=True)
ax.set_yticks(np.arange(-0.5, n_lin, 1), minor=True)
ax.grid(which='minor', color='white', lw=1.2)
ax.tick_params(which='both', length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

cbar = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
cbar.set_label('Probabilidade prevista de rebaixamento')
cbar.ax.yaxis.set_major_formatter(lambda v, _: f'{100 * v:.0f}%')

legenda = [Patch(fill=False, edgecolor='black', lw=1.8, label='Rebaixamento efetivo'),
           Patch(facecolor='#f2f2f2', edgecolor='#cccccc', label='Fora da Série A')]
ax.legend(handles=legenda, loc='lower left', bbox_to_anchor=(0, 1.01),
          ncol=2, frameon=False, fontsize=9)

fig.tight_layout()
for d in DIR_FIGS:
    os.makedirs(d, exist_ok=True)
    fig.savefig(os.path.join(d, 'heatmap_risco_longitudinal.png'),
                dpi=300, bbox_inches='tight')
print('[fig] heatmap_risco_longitudinal.png')

# Resumo no console: AUC por temporada retroativa
from sklearn.metrics import roc_auc_score
print('\nAUC-ROC retroativo por temporada (treino expansivo):')
for T in TEMPORADAS:
    sub = painel[painel['Temporada'] == T]
    if sub['rebaixado'].nunique() > 1:
        print(f'  {T}: {roc_auc_score(sub["rebaixado"], sub["prob"]):.3f}')
