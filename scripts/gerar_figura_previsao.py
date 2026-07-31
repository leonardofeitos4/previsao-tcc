# -*- coding: utf-8 -*-
"""Regenera previsao_2025_v2.png em 300 dpi e legível em escala de cinza.

Mesmo pipeline da Tabela 7 (logistica.pkl + scaler salvo + mediana do
treino <=2022). Diferenças em relação à versão do notebook 07: nomes com
acentos, 300 dpi e hachura nas barras da zona de rebaixamento --- a
identificação não depende apenas da cor (impressão em P&B).
"""
import os
import joblib
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

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
           'Gremio': 'Grêmio', 'Sao Paulo': 'São Paulo', 'Vitoria': 'Vitória'}


def construir_base():
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

    cols_merge = ['Clube', 'Temporada'] + FEATURES_JANELA
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
modelo = joblib.load(os.path.join(RAIZ, 'modelos', 'logistica.pkl'))
scaler = joblib.load(os.path.join(RAIZ, 'modelos', 'scaler_logistica.pkl'))

mediana = df[(df['Temporada'] <= 2022)][FEATURES_JANELA].median()
df_25 = df[df['Temporada'] == 2025].copy()
for col in FEATURES_JANELA:
    df_25[col] = df_25[col].fillna(mediana[col])
idx1 = list(modelo.classes_).index(1)
df_25['prob'] = modelo.predict_proba(scaler.transform(df_25[FEATURES]))[:, idx1]
df_25 = df_25.sort_values('prob', ascending=False).reset_index(drop=True)
assert abs(df_25.loc[0, 'prob'] - 0.7937) < 0.01, 'Tabela 7 nao reproduzida!'

VERMELHO, AZUL = '#e53935', '#1e3d59'
clubes = [ACENTOS.get(c, c) for c in df_25['Clube']][::-1]
probs = (100 * df_25['prob'])[::-1].values
rebaixado = [i < 4 for i in range(len(df_25))][::-1]  # top-4 risco (df ordenado desc.)

fig, ax = plt.subplots(figsize=(11, 9))
bars = ax.barh(clubes, probs,
               color=[VERMELHO if r else AZUL for r in rebaixado],
               hatch=['///' if r else '' for r in rebaixado],
               edgecolor='white', height=0.7)
ax.axvline(x=50, color='gray', linestyle='--', alpha=0.6, label='Limiar 50%')
ax.set_xlabel('Probabilidade de rebaixamento (%)', fontsize=12)
ax.set_title('Previsão de Rebaixamento — Brasileirão Série A 2025',
             fontsize=14, fontweight='bold')
ax.set_xlim(0, 105)
for bar, val in zip(bars, probs):
    ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
            f'{val:.1f}%'.replace('.', ','), va='center', fontsize=9)
ax.legend(handles=[
    mpatches.Patch(facecolor=VERMELHO, hatch='///', edgecolor='white',
                   label='Zona de rebaixamento prevista (4 maiores riscos)'),
    mpatches.Patch(facecolor=AZUL, label='Permanência prevista na Série A'),
    plt.Line2D([0], [0], color='gray', linestyle='--', label='Limiar 50%'),
], loc='lower right', fontsize=10)
ax.grid(alpha=0.3, axis='x')
plt.tight_layout()
for d in DIR_FIGS:
    os.makedirs(d, exist_ok=True)
    fig.savefig(os.path.join(d, 'previsao_2025_v2.png'), dpi=300, bbox_inches='tight')
print('[fig] previsao_2025_v2.png (300 dpi, com hachura)')
