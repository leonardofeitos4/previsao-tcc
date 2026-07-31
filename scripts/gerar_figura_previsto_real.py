# -*- coding: utf-8 -*-
"""Figura "previsto x aconteceu" para a apresentação — gráfico de inclinação.

Liga o ranking de RISCO PREVISTO (esquerda) à CLASSIFICAÇÃO FINAL REAL de 2025
(direita). Os dois eixos são ordenados com o "pior" em cima, de modo que uma
linha horizontal = acerto de ordenação e uma linha cruzando = erro.

Fonte da classificação final de 2025: CBF (mesma usada na Tabela 9 do artigo).
A tabela de 2026 (campeonato em curso) NÃO entra aqui — ela é usada apenas no
slide do Mirassol.

Saída: tex/apresentacao/figuras/slide_previsto_real.png
"""
import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DIR_OUT = os.path.join(RAIZ, 'tex', 'apresentacao', 'figuras')

TARGET = 'Status_bin'
METRICAS = ['Pts', 'SG', 'Gols_Pro', 'Gols_Contra', 'V', 'Aproveitamento']
JANELAS = [3, 5]
FEATURES_ELENCO = ['Plantel', 'Estrangeiros', 'Valor de Mercado Total']
FEATURES_JANELA = [f'{m}_media_{w}' for m in METRICAS for w in JANELAS]
FEATURES = FEATURES_ELENCO + FEATURES_JANELA

AZUL, VERM, VERDE = '#0072B2', '#D55E00', '#009E73'
CINZA, CINZA_TXT = '#AEB8C2', '#333333'

ACENTOS = {'Atletico Mineiro': 'Atlético-MG', 'Ceara': 'Ceará', 'Gremio': 'Grêmio',
           'Sao Paulo': 'São Paulo', 'Vitoria': 'Vitória',
           'Vasco da Gama': 'Vasco', 'Bragantino': 'Bragantino',
           'Sport Recife': 'Sport'}

# Classificação final do Brasileirão 2025 (CBF)
POSICAO_REAL_2025 = {
    'Flamengo': 1, 'Palmeiras': 2, 'Cruzeiro': 3, 'Mirassol': 4,
    'Fluminense': 5, 'Botafogo': 6, 'Bahia': 7, 'Sao Paulo': 8,
    'Gremio': 9, 'Bragantino': 10, 'Atletico Mineiro': 11, 'Santos': 12,
    'Corinthians': 13, 'Vasco da Gama': 14, 'Vitoria': 15,
    'Internacional': 16, 'Ceara': 17, 'Fortaleza': 18, 'Juventude': 19,
    'Sport Recife': 20,
}
REBAIXADOS = {'Ceara', 'Fortaleza', 'Juventude', 'Sport Recife'}

plt.rcParams.update({
    'font.size': 13, 'text.color': CINZA_TXT, 'figure.facecolor': 'white',
})


def construir_base():
    df = pd.read_excel(os.path.join(RAIZ, 'dados', 'processados', 'BASE_FINAL.xlsx'),
                       sheet_name='CLUBES')
    df.columns = df.columns.str.strip()
    df[TARGET] = df['Situacao'].apply(
        lambda x: 1 if str(x).strip().lower() == 'rebaixado' else 0)
    dd = pd.read_excel(os.path.join(RAIZ, 'dados', 'brutos',
                                    'tabela_desempenho_brasileirao.xlsx'),
                       sheet_name='Todos')
    dd.columns = dd.columns.str.strip()
    dd = dd.sort_values(['Clube', 'Temporada']).reset_index(drop=True)
    for m in METRICAS:
        for w in JANELAS:
            dd[f'{m}_media_{w}'] = (dd.groupby('Clube')[m]
                .transform(lambda x: x.shift(1).rolling(w, min_periods=1).mean()))
    cols = ['Clube', 'Temporada'] + FEATURES_JANELA
    rows = []
    for c in df['Clube'][df['Temporada'] == 2025].unique():
        h = dd[dd['Clube'] == c].sort_values('Temporada', ascending=False)
        r = {'Clube': c, 'Temporada': 2025}
        for m in METRICAS:
            for w in JANELAS:
                u = h.head(w)[m]
                r[f'{m}_media_{w}'] = u.mean() if len(u) else None
        rows.append(r)
    ext = pd.concat([dd[cols], pd.DataFrame(rows)[cols]], ignore_index=True)
    return df.merge(ext[cols], on=['Clube', 'Temporada'], how='left')


df = construir_base()
rot = df[df['Temporada'] < 2025]
med = rot[rot['Temporada'] <= 2022][FEATURES_JANELA].median()
modelo = joblib.load(os.path.join(RAIZ, 'modelos', 'logistica.pkl'))
scaler = joblib.load(os.path.join(RAIZ, 'modelos', 'scaler_logistica.pkl'))

d25 = df[df['Temporada'] == 2025].copy()
for c in FEATURES_JANELA:
    d25[c] = d25[c].fillna(med[c])
i1 = list(modelo.classes_).index(1)
d25['prob'] = modelo.predict_proba(scaler.transform(d25[FEATURES]))[:, i1]
d25 = d25.sort_values('prob', ascending=False).reset_index(drop=True)
assert abs(d25.loc[0, 'prob'] - 0.7937) < 0.01, 'Tabela 7 não reproduzida!'
d25['rank_prev'] = np.arange(1, len(d25) + 1)
d25['pos_real'] = d25['Clube'].map(POSICAO_REAL_2025)
d25['caiu'] = d25['Clube'].isin(REBAIXADOS)

# ── Gráfico de inclinação ───────────────────────────────────────────────────
# y = 1 em cima; à esquerda y = ranking de risco (1 = maior risco);
# à direita y = 21 - posição final (20.º em cima) => "pior em cima" nos dois lados.
fig, ax = plt.subplots(figsize=(11.5, 6.6))
XL, XR = 0.0, 1.0

# Faixa da zona de rebaixamento (4 primeiros de cada lado)
ax.add_patch(Rectangle((XL - 0.055, 0.5), 0.11, 4, facecolor=VERM, alpha=0.07, zorder=0))
ax.add_patch(Rectangle((XR - 0.055, 0.5), 0.11, 4, facecolor=VERM, alpha=0.07, zorder=0))

for _, r in d25.iterrows():
    y_esq = r['rank_prev']
    y_dir = 21 - r['pos_real']
    caiu = r['caiu']
    mirassol = r['Clube'] == 'Mirassol'
    if caiu:
        cor, lw, alpha, ls, z = VERM, 2.8, 1.0, '-', 4
    elif mirassol:
        cor, lw, alpha, ls, z = VERDE, 2.6, 1.0, (0, (5, 2)), 4
    else:
        cor, lw, alpha, ls, z = CINZA, 1.6, 0.85, '-', 2
    ax.plot([XL, XR], [y_esq, y_dir], color=cor, lw=lw, alpha=alpha,
            ls=ls, zorder=z, solid_capstyle='round')
    ax.plot([XL, XR], [y_esq, y_dir], 'o', color=cor, ms=7, zorder=z + 1)

    nome = ACENTOS.get(r['Clube'], r['Clube'])
    peso = 'bold' if (caiu or mirassol) else 'normal'
    cor_txt = cor if (caiu or mirassol) else CINZA_TXT
    ax.text(XL - 0.022, y_esq, f'{int(y_esq)}. {nome}', ha='right', va='center',
            fontsize=12.5, fontweight=peso, color=cor_txt, zorder=6)
    ax.text(XR + 0.022, y_dir, f'{nome}  ({int(r["pos_real"])}º)',
            ha='left', va='center', fontsize=12.5, fontweight=peso,
            color=cor_txt, zorder=6)

ax.set_xlim(-0.42, 1.42)
ax.set_ylim(20.8, 0.2)
ax.set_xticks([])
ax.set_yticks([])
for s in ax.spines.values():
    s.set_visible(False)

ax.text(XL, -0.55, 'O QUE EU PREVI', ha='center', fontsize=15,
        fontweight='bold', color=AZUL)
ax.text(XL, 0.05, 'ranking de risco (1 = maior)', ha='center', fontsize=11.5,
        color='#777777')
ax.text(XR, -0.55, 'O QUE ACONTECEU', ha='center', fontsize=15,
        fontweight='bold', color=AZUL)
ax.text(XR, 0.05, 'classificação final de 2025', ha='center', fontsize=11.5,
        color='#777777')

ax.legend(handles=[
    Line2D([0], [0], color=VERM, lw=2.8, label='Rebaixado de fato'),
    Line2D([0], [0], color=VERDE, lw=2.6, ls=(0, (5, 2)), label='Mirassol (outlier)'),
    Patch(facecolor=VERM, alpha=0.14, label='Zona de rebaixamento (4)'),
], loc='lower center', bbox_to_anchor=(0.5, -0.115), ncol=3, frameon=False,
    fontsize=12.5)

fig.tight_layout()
os.makedirs(DIR_OUT, exist_ok=True)
fig.savefig(os.path.join(DIR_OUT, 'slide_previsto_real.png'), dpi=200,
            bbox_inches='tight', facecolor='white')
plt.close(fig)
print('[fig] slide_previsto_real.png')

# Resumo no console
print('\nprevisto (top 4):', [ACENTOS.get(c, c) for c in d25.head(4)['Clube']])
print('caiu de fato:    ', sorted(ACENTOS.get(c, c) for c in REBAIXADOS))
print('acertos no corte:', len(set(d25.head(4)['Clube']) & REBAIXADOS))
for _, r in d25.head(8).iterrows():
    print(f'  {r["rank_prev"]:2d}. {ACENTOS.get(r["Clube"], r["Clube"]):<12} '
          f'{100*r["prob"]:5.1f}%  -> {int(r["pos_real"]):2d}º '
          f'{"REBAIXADO" if r["caiu"] else ""}')
