# -*- coding: utf-8 -*-
"""Gera as figuras da APRESENTAÇÃO (tex/apresentacao/figuras).

Não substitui as figuras do artigo: são versões para projetor --- fontes
grandes, menos elementos por gráfico e rótulos diretos. Mesmo pipeline e
mesmos modelos salvos, então os números coincidem com o artigo.

Paleta categórica validada para daltonismo (Okabe-Ito), com marcadores
distintos por modelo como codificação redundante à cor:
  Regressão Logística #0072B2 (o)   LightGBM      #D55E00 (s)
  Random Forest       #009E73 (^)   XGBoost       #CC79A7 (D)
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
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DIR_OUT = os.path.join(RAIZ, 'tex', 'apresentacao', 'figuras')

TARGET = 'Status_bin'
METRICAS = ['Pts', 'SG', 'Gols_Pro', 'Gols_Contra', 'V', 'Aproveitamento']
JANELAS = [3, 5]
FEATURES_ELENCO = ['Plantel', 'Estrangeiros', 'Valor de Mercado Total']
FEATURES_JANELA = [f'{m}_media_{w}' for m in METRICAS for w in JANELAS]
FEATURES = FEATURES_ELENCO + FEATURES_JANELA

AZUL, VERM, VERDE, ROXO = '#0072B2', '#D55E00', '#009E73', '#CC79A7'
CINZA_TXT = '#333333'
ESTILO = {  # cor + marcador (codificação redundante)
    'Regressao Logistica': (AZUL, 'o', 'Regressão Logística'),
    'Random Forest':       (VERDE, '^', 'Random Forest'),
    'XGBoost':             (ROXO, 'D', 'XGBoost'),
    'LightGBM':            (VERM, 's', 'LightGBM'),
}

ACENTOS = {'Atletico Mineiro': 'Atlético Mineiro', 'Ceara': 'Ceará',
           'Gremio': 'Grêmio', 'Sao Paulo': 'São Paulo', 'Vitoria': 'Vitória',
           'America Mineiro': 'América Mineiro',
           'Atletico Goianiense': 'Atlético-GO', 'Avai': 'Avaí',
           'Criciuma': 'Criciúma', 'Cuiaba': 'Cuiabá', 'Goias': 'Goiás',
           'Parana': 'Paraná'}

POSICAO_REAL_2025 = {
    'Flamengo': 1, 'Palmeiras': 2, 'Cruzeiro': 3, 'Mirassol': 4,
    'Fluminense': 5, 'Botafogo': 6, 'Bahia': 7, 'Sao Paulo': 8,
    'Gremio': 9, 'Bragantino': 10, 'Atletico Mineiro': 11, 'Santos': 12,
    'Corinthians': 13, 'Vasco da Gama': 14, 'Vitoria': 15,
    'Internacional': 16, 'Ceara': 17, 'Fortaleza': 18, 'Juventude': 19,
    'Sport Recife': 20,
}
REBAIXADOS_2025 = {'Ceara', 'Fortaleza', 'Juventude', 'Sport Recife'}

plt.rcParams.update({
    'font.size': 15, 'axes.titlesize': 17, 'axes.labelsize': 15,
    'xtick.labelsize': 14, 'ytick.labelsize': 14, 'legend.fontsize': 13,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.edgecolor': '#999999', 'text.color': CINZA_TXT,
    'axes.labelcolor': CINZA_TXT, 'xtick.color': CINZA_TXT,
    'ytick.color': CINZA_TXT, 'figure.facecolor': 'white',
})


def salvar(fig, nome):
    os.makedirs(DIR_OUT, exist_ok=True)
    fig.savefig(os.path.join(DIR_OUT, nome), dpi=200, bbox_inches='tight',
                facecolor='white')
    plt.close(fig)
    print(f'[fig] {nome}')


def virg(x, dec=3):
    return f'{x:.{dec}f}'.replace('.', ',')


# ── Base (idêntica aos scripts do artigo) ────────────────────────────────────
def construir_base(janelas=(3, 5)):
    cols_janela = [f'{m}_media_{w}' for m in METRICAS for w in janelas]
    df = pd.read_excel(os.path.join(RAIZ, 'dados', 'processados', 'BASE_FINAL.xlsx'),
                       sheet_name='CLUBES')
    df.columns = df.columns.str.strip()
    df[TARGET] = df['Situacao'].apply(
        lambda x: 1 if str(x).strip().lower() == 'rebaixado' else 0)

    df_d = pd.read_excel(os.path.join(RAIZ, 'dados', 'brutos',
                                      'tabela_desempenho_brasileirao.xlsx'),
                         sheet_name='Todos')
    df_d.columns = df_d.columns.str.strip()
    df_d = df_d.sort_values(['Clube', 'Temporada']).reset_index(drop=True)
    for m in METRICAS:
        for w in janelas:
            df_d[f'{m}_media_{w}'] = (
                df_d.groupby('Clube')[m]
                .transform(lambda x: x.shift(1).rolling(window=w, min_periods=1).mean()))

    cols = ['Clube', 'Temporada'] + cols_janela
    rows_25 = []
    for clube in df['Clube'][df['Temporada'] == 2025].unique():
        hist = df_d[df_d['Clube'] == clube].sort_values('Temporada', ascending=False)
        row = {'Clube': clube, 'Temporada': 2025}
        for m in METRICAS:
            for w in janelas:
                u = hist.head(w)[m]
                row[f'{m}_media_{w}'] = u.mean() if len(u) > 0 else None
        rows_25.append(row)
    df_ext = pd.concat([df_d[cols], pd.DataFrame(rows_25)[cols]], ignore_index=True)
    return df.merge(df_ext[cols], on=['Clube', 'Temporada'], how='left')


df = construir_base()
df_rot = df[df['Temporada'] < 2025].copy()
df_tr = df_rot[df_rot['Temporada'] <= 2022].copy()
df_te = df_rot[df_rot['Temporada'] > 2022].copy()
med_tr = df_tr[FEATURES_JANELA].median()
for c in FEATURES_JANELA:
    df_tr[c] = df_tr[c].fillna(med_tr[c])
    df_te[c] = df_te[c].fillna(med_tr[c])
sc = StandardScaler()
X_tr, y_tr = sc.fit_transform(df_tr[FEATURES]), df_tr[TARGET].values
X_te, y_te = sc.transform(df_te[FEATURES]), df_te[TARGET].values

ARQ = {'Regressao Logistica': 'regressao_logistica.pkl',
       'Random Forest': 'random_forest.pkl',
       'XGBoost': 'xgboost.pkl', 'LightGBM': 'lightgbm.pkl'}
modelos = {n: joblib.load(os.path.join(RAIZ, 'modelos', f)) for n, f in ARQ.items()}
res = {}
for n, clf in modelos.items():
    yp, pr = clf.predict(X_te), clf.predict_proba(X_te)[:, 1]
    res[n] = {'acc': (yp == y_te).mean(), 'auc': roc_auc_score(y_te, pr),
              'y_pred': yp, 'y_prob': pr}
    print(f'{n:<22} acc={res[n]["acc"]:.3f}  auc={res[n]["auc"]:.3f}')

# ── 1. Walk-forward por fold ────────────────────────────────────────────────
BASE = {
    'Regressao Logistica': LogisticRegression(C=1.0, random_state=42, max_iter=1000,
                                              class_weight='balanced'),
    'Random Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced',
                                            random_state=42),
    'XGBoost': XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss',
                             scale_pos_weight=4, verbosity=0),
    'LightGBM': LGBMClassifier(n_estimators=100, random_state=42,
                               class_weight='balanced', verbose=-1),
}
temps = sorted(df_tr['Temporada'].unique())
N_F = 5
ini = len(temps) - N_F
wf = {n: [] for n in BASE}
anos_val = []
for i in range(N_F):
    anos_tr, ano_v = temps[:ini + i], temps[ini + i]
    anos_val.append(ano_v)
    d_tr = df_rot[df_rot['Temporada'].isin(anos_tr)].copy()
    d_v = df_rot[df_rot['Temporada'] == ano_v].copy()
    m_ = d_tr[FEATURES_JANELA].median()
    for c in FEATURES_JANELA:
        d_tr[c] = d_tr[c].fillna(m_[c])
        d_v[c] = d_v[c].fillna(m_[c])
    s_ = StandardScaler()
    Xf, Xv = s_.fit_transform(d_tr[FEATURES]), s_.transform(d_v[FEATURES])
    for n, clf in BASE.items():
        clf.fit(Xf, d_tr[TARGET].values)
        wf[n].append(roc_auc_score(d_v[TARGET].values, clf.predict_proba(Xv)[:, 1]))

fig, ax = plt.subplots(figsize=(11, 5.9))
for n, aucs in wf.items():
    cor, mk, rot = ESTILO[n]
    ax.plot(range(1, N_F + 1), aucs, marker=mk, lw=2.5, ms=10, color=cor,
            label=f'{rot}  ({virg(np.mean(aucs))} ± {virg(np.std(aucs))})')
ax.axhline(0.5, color='#999999', ls=':', lw=1.5)
ax.text(1.0, 0.515, 'classificador aleatório', va='bottom', ha='left',
        fontsize=12, color='#777777')
ax.annotate('2020: pandemia', xy=(3, 0.432), xytext=(2.1, 0.335),
            fontsize=13.5, color=CINZA_TXT, ha='center',
            arrowprops=dict(arrowstyle='->', color='#777777', lw=1.4,
                            connectionstyle='arc3,rad=-0.2'))
ax.set_xlabel('Temporada de validação')
ax.set_ylabel('AUC-ROC')
ax.set_xticks(range(1, N_F + 1))
ax.set_xticklabels([str(a) for a in anos_val])
ax.set_ylim(0.28, 0.98)
ax.set_xlim(0.9, N_F + 0.15)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2,
          frameon=False, columnspacing=2.4, handletextpad=0.6)
ax.grid(alpha=0.25, axis='y')
salvar(fig, 'slide_walkforward.png')

# ── 2. Curvas ROC no teste ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8.2, 6.4))
ordem = sorted(res, key=lambda n: -res[n]['auc'])
for n in ordem:
    cor, mk, rot = ESTILO[n]
    fpr, tpr, _ = roc_curve(y_te, res[n]['y_prob'])
    ax.plot(fpr, tpr, lw=3, color=cor, label=f'{rot} — {virg(res[n]["auc"])}')
ax.plot([0, 1], [0, 1], ls='--', lw=1.5, color='#999999', label='Aleatório — 0,500')
ax.set_xlabel('Taxa de falsos positivos')
ax.set_ylabel('Taxa de verdadeiros positivos')
ax.legend(loc='lower right', frameon=False)
ax.grid(alpha=0.25)
salvar(fig, 'slide_roc.png')

# ── 3. A armadilha da acurácia ──────────────────────────────────────────────
# ATENÇÃO: as matrizes de confusão do XGBoost e do LightGBM são IDÊNTICAS
# ([[3,5],[2,30]], acurácia 82,5% nos dois). Logo a matriz não explica o
# vão de AUC --- ele está inteiramente na ORDENAÇÃO das probabilidades.
# Esta figura mostra onde caem os 8 rebaixados no ranking de risco de cada
# modelo: o LightGBM concentra-os à esquerda; o XGBoost os espalha.
cm_x = confusion_matrix(y_te, res['XGBoost']['y_pred'], labels=[1, 0])
cm_l = confusion_matrix(y_te, res['LightGBM']['y_pred'], labels=[1, 0])
assert (cm_x == cm_l).all(), 'matrizes deixaram de ser idênticas'
print(f'\n[!] matriz de confusão idêntica nos dois modelos: {cm_x.tolist()}')

fig, axes = plt.subplots(2, 1, figsize=(11.5, 4.6), sharex=True)
n_te = len(y_te)
for ax, n in zip(axes, ['LightGBM', 'XGBoost']):
    cor = ESTILO[n][0]
    ordem = np.argsort(-res[n]['y_prob'])
    y_ord = y_te[ordem]
    pos_reb = [i + 1 for i, v in enumerate(y_ord) if v == 1]
    ax.scatter([i + 1 for i, v in enumerate(y_ord) if v == 0],
               [0] * (n_te - len(pos_reb)), s=110, marker='|',
               color='#C8CED4', linewidths=2.2)
    ax.scatter(pos_reb, [0] * len(pos_reb), s=250, marker='v', color=cor,
               edgecolors='white', linewidths=1.2, zorder=3)
    for p in pos_reb:
        ax.text(p, 0.34, str(p), ha='center', fontsize=12, color=cor,
                fontweight='bold')
    ax.set_ylim(-0.55, 0.78)
    ax.set_xlim(0, n_te + 1)
    ax.set_yticks([])
    ax.text(-0.008, 0.5, n, transform=ax.transAxes, ha='right', va='center',
            fontsize=16, fontweight='bold', color=cor)
    ax.annotate(f'AUC {virg(res[n]["auc"])}', xy=(0.995, 0.06),
                xycoords='axes fraction', ha='right', va='bottom',
                fontsize=15, color=cor, fontweight='bold')
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
axes[1].set_xlabel('Posição no ranking de risco previsto  '
                   '(1 = maior risco  →  40 = menor risco)')
axes[1].tick_params(labelbottom=True, labelsize=13)
axes[0].annotate('os 8 clubes rebaixados de fato', xy=(0.5, 1.30),
                 xycoords='axes fraction', ha='center', fontsize=13.5,
                 color=CINZA_TXT)
fig.tight_layout()
salvar(fig, 'slide_armadilha.png')

# ── 4. O que pesa: coeficientes da logística (top 8 em módulo) ──────────────
rl_final = joblib.load(os.path.join(RAIZ, 'modelos', 'logistica.pkl'))
coefs = pd.Series(rl_final.coef_[0], index=FEATURES)
top = coefs.reindex(coefs.abs().sort_values(ascending=False).index).head(8)
top = top.sort_values()
NOMES = {'Valor de Mercado Total': 'Valor de mercado do elenco',
         'Plantel': 'Tamanho do plantel', 'Estrangeiros': 'N.º de estrangeiros',
         'V_media_3': 'Vitórias — média 3 temp.', 'V_media_5': 'Vitórias — média 5 temp.',
         'Pts_media_3': 'Pontos — média 3 temp.', 'Pts_media_5': 'Pontos — média 5 temp.',
         'SG_media_3': 'Saldo de gols — média 3 temp.',
         'SG_media_5': 'Saldo de gols — média 5 temp.',
         'Gols_Pro_media_3': 'Gols marcados — média 3 temp.',
         'Gols_Pro_media_5': 'Gols marcados — média 5 temp.',
         'Gols_Contra_media_3': 'Gols sofridos — média 3 temp.',
         'Gols_Contra_media_5': 'Gols sofridos — média 5 temp.',
         'Aproveitamento_media_3': 'Aproveitamento — média 3 temp.',
         'Aproveitamento_media_5': 'Aproveitamento — média 5 temp.'}
fig, ax = plt.subplots(figsize=(11, 5.4))
cores = [VERM if v > 0 else AZUL for v in top.values]
ax.barh([NOMES.get(i, i) for i in top.index], top.values, color=cores, height=0.68)
ax.axvline(0, color=CINZA_TXT, lw=1.2)
for y, v in enumerate(top.values):
    ax.text(v + (0.035 if v > 0 else -0.035), y, virg(v, 3),
            va='center', ha='left' if v > 0 else 'right', fontsize=13)
ax.set_xlabel('Coeficiente padronizado  (log-odds de rebaixamento)')
ax.set_xlim(-1.25, 0.95)
ax.legend(handles=[Patch(facecolor=VERM, label='Aumenta o risco'),
                   Patch(facecolor=AZUL, label='Protege')],
          loc='lower right', frameon=False)
ax.grid(alpha=0.25, axis='x')
salvar(fig, 'slide_importancia.png')

# ── 5. Previsão 2025 (top 10, hachura na zona) ──────────────────────────────
scaler_f = joblib.load(os.path.join(RAIZ, 'modelos', 'scaler_logistica.pkl'))
df_25 = df[df['Temporada'] == 2025].copy()
for c in FEATURES_JANELA:
    df_25[c] = df_25[c].fillna(med_tr[c])
i1 = list(rl_final.classes_).index(1)
df_25['prob'] = rl_final.predict_proba(scaler_f.transform(df_25[FEATURES]))[:, i1]
df_25 = df_25.sort_values('prob', ascending=False).reset_index(drop=True)
assert abs(df_25.loc[0, 'prob'] - 0.7937) < 0.01, 'Tabela 7 não reproduzida!'

t10 = df_25.head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(10.5, 5.6))
zona = [i >= 6 for i in range(10)]  # invertido: 4 primeiros do ranking
bars = ax.barh([ACENTOS.get(c, c) for c in t10['Clube']], 100 * t10['prob'],
               color=[VERM if z else '#B9C6D1' for z in zona],
               hatch=['///' if z else '' for z in zona],
               edgecolor='white', height=0.7)
ax.axvline(50, color='#888888', ls='--', lw=1.5)
ax.text(50.8, 9.62, 'limiar 50%', fontsize=12.5, color='#777777', va='center')
for b, v in zip(bars, 100 * t10['prob']):
    ax.text(b.get_width() + 1.1, b.get_y() + b.get_height() / 2,
            f'{virg(v, 1)}%', va='center', fontsize=14)
ax.set_xlabel('Probabilidade prevista de rebaixamento (%)')
ax.set_xlim(0, 100)
ax.legend(handles=[Patch(facecolor=VERM, hatch='///', edgecolor='white',
                         label='Zona de rebaixamento prevista')],
          loc='lower right', frameon=False)
ax.grid(alpha=0.25, axis='x')
salvar(fig, 'slide_previsao2025.png')

# ── 6. A prova real: previsto x aconteceu ───────────────────────────────────
t10b = df_25.head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(11, 5.8))
rot_y, cores_b, hat = [], [], []
for c in t10b['Clube']:
    caiu = c in REBAIXADOS_2025
    rot_y.append(f"{ACENTOS.get(c, c)}  ({POSICAO_REAL_2025[c]}º)")
    cores_b.append(VERM if caiu else '#B9C6D1')
    hat.append('///' if caiu else '')
bars = ax.barh(rot_y, 100 * t10b['prob'], color=cores_b, hatch=hat,
               edgecolor='white', height=0.7)
for b, v, c in zip(bars, 100 * t10b['prob'], t10b['Clube']):
    caiu = c in REBAIXADOS_2025
    ax.text(b.get_width() + 1.1, b.get_y() + b.get_height() / 2,
            f'{virg(v, 1)}%' + ('  ✔' if caiu else ''),
            va='center', fontsize=14,
            fontweight='bold' if caiu else 'normal')
ax.axhline(5.5, color=CINZA_TXT, lw=1.6, ls='--')
ax.text(99, 5.62, 'corte previsto (top 4)', ha='right', fontsize=12.5,
        color=CINZA_TXT)
ax.set_xlabel('Probabilidade prevista de rebaixamento (%)   ·   (  º ) = posição final real')
ax.set_xlim(0, 100)
ax.legend(handles=[Patch(facecolor=VERM, hatch='///', edgecolor='white',
                         label='Rebaixado de fato em 2025')],
          loc='lower right', frameon=False)
ax.grid(alpha=0.25, axis='x')
salvar(fig, 'slide_validacao.png')

# ── 7. Mapa de calor longitudinal (recorte de 16 clubes) ────────────────────
regs = []
for T in range(2016, 2026):
    tr = df[(df['Temporada'] < T) & (df['Temporada'] < 2025)].copy()
    al = df[df['Temporada'] == T].copy()
    m_ = tr[FEATURES_JANELA].median()
    for c in FEATURES_JANELA:
        tr[c] = tr[c].fillna(m_[c])
        al[c] = al[c].fillna(m_[c])
    s_ = StandardScaler().fit(tr[FEATURES])
    mm = clone(rl_final)
    mm.fit(s_.transform(tr[FEATURES]), tr[TARGET].values)
    k1 = list(mm.classes_).index(1)
    al['prob'] = mm.predict_proba(s_.transform(al[FEATURES]))[:, k1]
    al['reb'] = (al['Clube'].isin(REBAIXADOS_2025).astype(int) if T == 2025
                 else al[TARGET])
    regs.append(al[['Clube', 'Temporada', 'prob', 'reb']])
pan = pd.concat(regs, ignore_index=True)
mp = pan.pivot(index='Clube', columns='Temporada', values='prob')
mr = pan.pivot(index='Clube', columns='Temporada', values='reb')
ordem_risco = mp.mean(axis=1).sort_values(ascending=False).index
sel = list(ordem_risco[:12]) + list(ordem_risco[-4:])   # 12 maiores + 4 menores
mp, mr = mp.loc[sel], mr.loc[sel]

n_l, n_c = mp.shape
fig, ax = plt.subplots(figsize=(11.5, 6.4))
im = ax.imshow(mp.values, cmap='Reds', vmin=0, vmax=1, aspect='auto')
ax.set_xticks(range(n_c)); ax.set_xticklabels(mp.columns, fontsize=13)
ax.set_yticks(range(n_l))
ax.set_yticklabels([ACENTOS.get(c, c) for c in mp.index], fontsize=12.5)
for i in range(n_l):
    for j in range(n_c):
        p = mp.values[i, j]
        if np.isnan(p):
            ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, facecolor='#f0f0f0',
                                   edgecolor='white', lw=.8, zorder=2))
            continue
        ax.text(j, i, f'{100*p:.0f}', ha='center', va='center', fontsize=10.5,
                color='white' if p > .55 else CINZA_TXT, zorder=4)
        if mr.values[i, j] == 1:
            ax.add_patch(Rectangle((j - .47, i - .47), .94, .94, fill=False,
                                   edgecolor='black', lw=2.2, zorder=5))
ax.set_xticks(np.arange(-.5, n_c, 1), minor=True)
ax.set_yticks(np.arange(-.5, n_l, 1), minor=True)
ax.grid(which='minor', color='white', lw=1.4)
ax.tick_params(which='both', length=0)
for s in ax.spines.values():
    s.set_visible(False)
cb = fig.colorbar(im, ax=ax, shrink=.75, pad=.015)
cb.set_label('Risco previsto', fontsize=13)
cb.ax.yaxis.set_major_formatter(lambda v, _: f'{100*v:.0f}%')
cb.ax.tick_params(labelsize=12)
ax.legend(handles=[Patch(fill=False, edgecolor='black', lw=2.2,
                         label='Rebaixamento efetivo'),
                   Patch(facecolor='#f0f0f0', edgecolor='#cccccc',
                         label='Fora da Série A')],
          loc='lower left', bbox_to_anchor=(0, 1.015), ncol=2, frameon=False,
          fontsize=12.5)
salvar(fig, 'slide_heatmap.png')

print('\nConcluído — figuras em tex/apresentacao/figuras')
