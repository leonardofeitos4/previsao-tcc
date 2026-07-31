# -*- coding: utf-8 -*-
"""Gera as análises novas solicitadas no parecer do orientador (v2 -> v3).

Reproduz o pipeline dos notebooks (mesmas 15 features, mesma separação
temporal e mesma imputação por mediana do treino) e produz:

Figuras (resultados/figuras e tex/tcc_artigo/figuras, 200 dpi):
  - heatmap_correlacao.png       Matriz de correlação das 15 features
  - importancia_features.png     Coeficientes da logística + ganho do LightGBM
  - calibracao_logistica.png     Diagrama de confiabilidade no teste 2023-2024

Tabelas LaTeX (tex/tcc_artigo/tabelas):
  - tab_estatisticas_descritivas.tex   AED das 15 features
  - tab_validacao_2025.tex             Validação retroativa da previsão 2025

Console: AUC-ROC real 2025 (logística, LightGBM, baselines ingênuos),
análises de sensibilidade (imputação média vs. mediana, janelas 2/4,
subconjuntos de features).
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

from sklearn.base import clone
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from sklearn.calibration import calibration_curve

RNG = np.random.RandomState(42)
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DIR_FIGS = [os.path.join(RAIZ, 'resultados', 'figuras'),
            os.path.join(RAIZ, 'tex', 'tcc_artigo', 'figuras')]
DIR_TAB = os.path.join(RAIZ, 'tex', 'tcc_artigo', 'tabelas')

TARGET = 'Status_bin'
METRICAS = ['Pts', 'SG', 'Gols_Pro', 'Gols_Contra', 'V', 'Aproveitamento']
JANELAS = [3, 5]
FEATURES_ELENCO = ['Plantel', 'Estrangeiros', 'Valor de Mercado Total']
FEATURES_JANELA = [f'{m}_media_{w}' for m in METRICAS for w in JANELAS]
FEATURES = FEATURES_ELENCO + FEATURES_JANELA

ACENTOS = {'Atletico Mineiro': 'Atlético Mineiro', 'Ceara': 'Ceará',
           'Gremio': 'Grêmio', 'Sao Paulo': 'São Paulo', 'Vitoria': 'Vitória'}

# Resultado real do Brasileirão 2025 (fonte: CBF/Wikipédia)
POSICAO_REAL_2025 = {
    'Flamengo': 1, 'Palmeiras': 2, 'Cruzeiro': 3, 'Mirassol': 4,
    'Fluminense': 5, 'Botafogo': 6, 'Bahia': 7, 'Sao Paulo': 8,
    'Gremio': 9, 'Bragantino': 10, 'Atletico Mineiro': 11, 'Santos': 12,
    'Corinthians': 13, 'Vasco da Gama': 14, 'Vitoria': 15,
    'Internacional': 16, 'Ceara': 17, 'Fortaleza': 18, 'Juventude': 19,
    'Sport Recife': 20,
}
REBAIXADOS_REAIS = {'Ceara', 'Fortaleza', 'Juventude', 'Sport Recife'}


def salvar(fig, nome):
    for d in DIR_FIGS:
        os.makedirs(d, exist_ok=True)
        fig.savefig(os.path.join(d, nome), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'[fig] {nome}')


def construir_base(janelas=(3, 5)):
    """Reconstrói a base com janelas deslizantes (idêntica ao notebook 06/07)."""
    cols_janela = [f'{m}_media_{w}' for m in METRICAS for w in janelas]
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
        for w in janelas:
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
            for w in janelas:
                ultimos = hist.head(w)[m]
                row[f'{m}_media_{w}'] = ultimos.mean() if len(ultimos) > 0 else None
        rows_2025.append(row)
    df_ext = pd.concat([df_desemp[cols_merge], pd.DataFrame(rows_2025)[cols_merge]],
                       ignore_index=True)
    return df.merge(df_ext[cols_merge], on=['Clube', 'Temporada'], how='left'), cols_janela


df, _ = construir_base()
df_rot = df[df['Temporada'] < 2025].copy()          # 2014-2024 rotulado
df_2025 = df[df['Temporada'] == 2025].copy()

# ============================================================
# 1. AED — estatísticas descritivas (antes da imputação)
# ============================================================
linhas = []
for f in FEATURES:
    s = df_rot[f]
    linhas.append({'Feature': f, 'Media': s.mean(), 'DP': s.std(),
                   'Min': s.min(), 'Max': s.max(),
                   'PctNA': 100 * s.isna().mean()})
aed = pd.DataFrame(linhas)
print('\n=== AED (base rotulada 2014-2024, n=%d) ===' % len(df_rot))
print(aed.round(2).to_string(index=False))
print('Prevalencia de rebaixamento: %.1f%%' % (100 * df_rot[TARGET].mean()))

def esc(nome):
    return nome.replace('_', r'\_')

with open(os.path.join(DIR_TAB, 'tab_estatisticas_descritivas.tex'), 'w',
          encoding='utf-8') as fh:
    fh.write('\\begin{table}[htbp]\n    \\centering\n')
    fh.write('    \\caption[Estatísticas descritivas das \\textit{features}]'
             '{Estatísticas descritivas das 15 \\textit{features} na base '
             'rotulada (2014--2024, $n = %d$), antes da imputação de valores ausentes.}\n'
             % len(df_rot))
    fh.write('    \\label{tab:aed}\n    \\small\n')
    fh.write('    \\begin{tabular}{lrrrrr}\n        \\toprule\n')
    fh.write('        \\textbf{\\textit{Feature}} & \\textbf{Média} & \\textbf{DP} & '
             '\\textbf{Mín.} & \\textbf{Máx.} & \\textbf{\\% ausente} \\\\\n')
    fh.write('        \\midrule\n')
    for _, r in aed.iterrows():
        nome = esc(r['Feature'])
        if r['Feature'] == 'Valor de Mercado Total':
            nome += ' (M\\euro)'
        fh.write('        %s & %s & %s & %s & %s & %s \\\\\n' % (
            nome,
            ('%.2f' % r['Media']).replace('.', ','),
            ('%.2f' % r['DP']).replace('.', ','),
            ('%.1f' % r['Min']).replace('.', ','),
            ('%.1f' % r['Max']).replace('.', ','),
            ('%.1f' % r['PctNA']).replace('.', ',')))
    fh.write('        \\bottomrule\n    \\end{tabular}\n\n')
    fh.write('    \\vspace{2pt}\n    {\\small Fonte: Elaborado pelo autor (\\the\\year).}\n')
    fh.write('\\end{table}\n')
print('[tab] tab_estatisticas_descritivas.tex')

# Heatmap de correlação (após imputação com mediana da própria base rotulada,
# apenas para fins descritivos)
df_corr = df_rot[FEATURES].copy()
df_corr = df_corr.fillna(df_corr.median())
corr = df_corr.corr()
fig, ax = plt.subplots(figsize=(10.5, 9))
im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
labels = [f if f != 'Valor de Mercado Total' else 'Valor de Mercado' for f in FEATURES]
ax.set_xticks(range(len(labels))); ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(labels, fontsize=9)
for i in range(len(labels)):
    for j in range(len(labels)):
        v = corr.values[i, j]
        ax.text(j, i, f'{v:.2f}'.replace('.', ','), ha='center', va='center',
                fontsize=6.5, color='white' if abs(v) > 0.6 else 'black')
fig.colorbar(im, ax=ax, shrink=0.8, label='Correlação de Pearson')
fig.tight_layout()
salvar(fig, 'heatmap_correlacao.png')

# ============================================================
# 2. Feature importance — coeficientes RL + ganho LightGBM
# ============================================================
modelo_final = joblib.load(os.path.join(RAIZ, 'modelos', 'logistica.pkl'))
scaler_final = joblib.load(os.path.join(RAIZ, 'modelos', 'scaler_logistica.pkl'))
lgbm_otim = joblib.load(os.path.join(RAIZ, 'modelos', 'lightgbm.pkl'))
print('\nModelo final carregado: %s' % type(modelo_final).__name__)
print('Hiperparametros LightGBM salvos: %s' % {k: v for k, v in
      lgbm_otim.get_params().items() if k in ('n_estimators', 'learning_rate',
      'max_depth', 'num_leaves', 'class_weight')})

coefs = pd.Series(modelo_final.coef_[0], index=FEATURES).sort_values()
ganho = pd.Series(lgbm_otim.booster_.feature_importance(importance_type='gain'),
                  index=FEATURES).sort_values()

fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
cores_coef = ['#e53935' if c > 0 else '#1e3d59' for c in coefs]
axes[0].barh([l.replace('Valor de Mercado Total', 'Valor de Mercado') for l in coefs.index],
             coefs.values, color=cores_coef)
axes[0].axvline(0, color='black', lw=0.8)
axes[0].set_title('(a) Regressão Logística — coeficientes padronizados')
axes[0].set_xlabel('Coeficiente (features padronizadas)')
axes[0].grid(alpha=0.3, axis='x')
axes[1].barh([l.replace('Valor de Mercado Total', 'Valor de Mercado') for l in ganho.index],
             ganho.values, color='#f57c00')
axes[1].set_title('(b) LightGBM — importância por ganho')
axes[1].set_xlabel('Ganho acumulado nas divisões')
axes[1].grid(alpha=0.3, axis='x')
fig.tight_layout()
salvar(fig, 'importancia_features.png')

print('\nCoeficientes da Regressao Logistica (ordenados):')
for f, c in coefs.sort_values(ascending=False).items():
    print(f'  {f:<28} {c:+.3f}')
print('\nImportancia LightGBM (gain, top 8):')
for f, g in ganho.sort_values(ascending=False).head(8).items():
    print(f'  {f:<28} {g:,.1f}')

# ============================================================
# 3. Previsão 2025 — RL (ponto + IC bootstrap) e LightGBM
# ============================================================
# Ponto: exatamente como no notebook 07 (mediana do treino <=2022, scaler salvo)
df_treino_07 = df_rot[df_rot['Temporada'] <= 2022]
mediana_07 = df_treino_07[FEATURES_JANELA].median()
df_25 = df_2025.copy()
for col in FEATURES_JANELA:
    df_25[col] = df_25[col].fillna(mediana_07[col])
X25 = scaler_final.transform(df_25[FEATURES])
idx1 = list(modelo_final.classes_).index(1)
df_25['prob_rl'] = modelo_final.predict_proba(X25)[:, idx1]

# Confere reprodução da Tabela 7 (Juventude 79.4, Sport 76.9, Vitoria 76.7)
chk = df_25.set_index('Clube')['prob_rl']
assert abs(chk['Juventude'] - 0.7937) < 0.01, 'Tabela 7 nao reproduzida!'
print('\n[ok] Probabilidades da Tabela 7 reproduzidas com logistica.pkl')

# LightGBM treinado em 2014-2024 (mesmos hiperparametros otimizados)
df_full = df_rot.copy()
for col in FEATURES_JANELA:
    df_full[col] = df_full[col].fillna(mediana_07[col])
sc_full = StandardScaler().fit(df_full[FEATURES])
lgbm_full = clone(lgbm_otim)
lgbm_full.fit(sc_full.transform(df_full[FEATURES]), df_full[TARGET].values)
idx1_l = list(lgbm_full.classes_).index(1)
df_25['prob_lgbm'] = lgbm_full.predict_proba(sc_full.transform(df_25[FEATURES]))[:, idx1_l]

# IC 95% via bootstrap (reamostragem da base rotulada, pipeline completo)
B = 1000
boot = np.empty((B, len(df_25)))
base_vals = df_rot.reset_index(drop=True)
for b in range(B):
    amostra = base_vals.sample(n=len(base_vals), replace=True, random_state=RNG)
    if amostra[TARGET].nunique() < 2:
        boot[b] = np.nan
        continue
    med_b = amostra[amostra['Temporada'] <= 2022][FEATURES_JANELA].median()
    med_b = med_b.fillna(amostra[FEATURES_JANELA].median())
    am = amostra.copy()
    d25 = df_2025.copy()
    for col in FEATURES_JANELA:
        am[col] = am[col].fillna(med_b[col])
        d25[col] = d25[col].fillna(med_b[col])
    sc_b = StandardScaler().fit(am[FEATURES])
    m_b = clone(modelo_final)
    m_b.fit(sc_b.transform(am[FEATURES]), am[TARGET].values)
    i1 = list(m_b.classes_).index(1)
    boot[b] = m_b.predict_proba(sc_b.transform(d25[FEATURES]))[:, i1]
ic_lo = np.nanpercentile(boot, 2.5, axis=0)
ic_hi = np.nanpercentile(boot, 97.5, axis=0)
df_25['ic_lo'], df_25['ic_hi'] = ic_lo, ic_hi

# ============================================================
# 4. Validação retroativa 2025
# ============================================================
df_25['pos_real'] = df_25['Clube'].map(POSICAO_REAL_2025)
df_25['reb_real'] = df_25['Clube'].isin(REBAIXADOS_REAIS).astype(int)
df_25 = df_25.sort_values('prob_rl', ascending=False).reset_index(drop=True)
df_25.index += 1

y_real = df_25['reb_real'].values
auc_rl = roc_auc_score(y_real, df_25['prob_rl'])
auc_lgbm = roc_auc_score(y_real, df_25['prob_lgbm'])
top4_rl = set(df_25.head(4)['Clube'])
top4_lgbm = set(df_25.sort_values('prob_lgbm', ascending=False).head(4)['Clube'])
acertos_rl = top4_rl & REBAIXADOS_REAIS
acertos_lgbm = top4_lgbm & REBAIXADOS_REAIS

# Baselines ingênuos
bl_valor = set(df_25.nsmallest(4, 'Valor de Mercado Total')['Clube'])
auc_valor = roc_auc_score(y_real, -df_25['Valor de Mercado Total'])
bl_pts = set(df_25.nsmallest(4, 'Pts_media_3')['Clube'])
auc_pts = roc_auc_score(y_real, -df_25['Pts_media_3'])

print('\n=== VALIDACAO RETROATIVA 2025 ===')
print('Rebaixados reais: %s' % sorted(REBAIXADOS_REAIS))
print('Top-4 RL:    %s | acertos: %d/4 (%s)' % (sorted(top4_rl), len(acertos_rl), sorted(acertos_rl)))
print('Top-4 LGBM:  %s | acertos: %d/4 (%s)' % (sorted(top4_lgbm), len(acertos_lgbm), sorted(acertos_lgbm)))
print('AUC-ROC real 2025 — RL:   %.3f' % auc_rl)
print('AUC-ROC real 2025 — LGBM: %.3f' % auc_lgbm)
print('Baseline menor valor de elenco: %s | acertos: %d/4 | AUC: %.3f'
      % (sorted(bl_valor), len(bl_valor & REBAIXADOS_REAIS), auc_valor))
print('Baseline pior Pts_media_3:      %s | acertos: %d/4 | AUC: %.3f'
      % (sorted(bl_pts), len(bl_pts & REBAIXADOS_REAIS), auc_pts))
print('\nRanking RL x realidade:')
for i, r in df_25.iterrows():
    print('  %2d. %-18s RL %5.1f%% [%4.1f-%5.1f] LGBM %5.1f%%  pos.real %2d  %s' % (
        i, r['Clube'], 100*r['prob_rl'], 100*r['ic_lo'], 100*r['ic_hi'],
        100*r['prob_lgbm'], r['pos_real'],
        'REBAIXADO' if r['reb_real'] else 'permaneceu'))

# Tabela LaTeX de validação
def pct(v):
    return ('%.1f' % (100 * v)).replace('.', ',')

with open(os.path.join(DIR_TAB, 'tab_validacao_2025.tex'), 'w', encoding='utf-8') as fh:
    fh.write('\\begin{table}[htbp]\n    \\centering\n')
    fh.write('    \\caption[Validação retroativa da previsão 2025]'
             '{Validação retroativa da previsão 2025: probabilidades da '
             'Regressão Logística (com intervalos de confiança de 95\\% via '
             '\\textit{bootstrap}, $B = 1000$) e do LightGBM \\textit{versus} o '
             'resultado real do campeonato. Clubes em negrito foram efetivamente '
             'rebaixados.}\n')
    fh.write('    \\label{tab:validacao2025}\n    \\small\n')
    fh.write('    \\begin{tabular}{clcccc}\n        \\toprule\n')
    fh.write('        \\textbf{\\#} & \\textbf{Clube} & \\textbf{Prob. RL} & '
             '\\textbf{IC 95\\%} & \\textbf{Prob. LGBM} & \\textbf{Pos. real} \\\\\n')
    fh.write('        \\midrule\n')
    for i, r in df_25.iterrows():
        nome = ACENTOS.get(r['Clube'], r['Clube'])
        if r['reb_real']:
            nome = '\\textbf{%s}' % nome
        fh.write('        %d & %s & %s\\%% & [%s; %s] & %s\\%% & %d.\\textordmasculine{} \\\\\n'
                 % (i, nome, pct(r['prob_rl']), pct(r['ic_lo']), pct(r['ic_hi']),
                    pct(r['prob_lgbm']), r['pos_real']))
        if i == 4:
            fh.write('        \\midrule\n')
    fh.write('        \\bottomrule\n    \\end{tabular}\n\n')
    fh.write('    \\vspace{2pt}\n    {\\small Fonte: Elaborado pelo autor (\\the\\year), '
             'com resultados oficiais da CBF.}\n\\end{table}\n')
print('[tab] tab_validacao_2025.tex')

# ============================================================
# 5. Calibração no teste 2023-2024 (bônus)
# ============================================================
rl_otim = joblib.load(os.path.join(RAIZ, 'modelos', 'regressao_logistica.pkl'))
df_tr = df_rot[df_rot['Temporada'] <= 2022].copy()
df_te = df_rot[df_rot['Temporada'] > 2022].copy()
med_tr = df_tr[FEATURES_JANELA].median()
for col in FEATURES_JANELA:
    df_tr[col] = df_tr[col].fillna(med_tr[col])
    df_te[col] = df_te[col].fillna(med_tr[col])
sc_tr = StandardScaler().fit(df_tr[FEATURES])
y_te = df_te[TARGET].values
p_te = rl_otim.predict_proba(sc_tr.transform(df_te[FEATURES]))[:, 1]
frac_pos, prob_media = calibration_curve(y_te, p_te, n_bins=4, strategy='quantile')
fig, ax = plt.subplots(figsize=(6.5, 6))
ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Calibração perfeita')
ax.plot(prob_media, frac_pos, marker='o', lw=2, color='#1e3d59',
        label='Regressão Logística')
ax.set_xlabel('Probabilidade média prevista')
ax.set_ylabel('Fração observada de rebaixados')
ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout()
salvar(fig, 'calibracao_logistica.png')
print('Calibracao (teste 2023-24): previsto=%s observado=%s'
      % (np.round(prob_media, 3), np.round(frac_pos, 3)))

# ============================================================
# 6. Análises de sensibilidade rápidas (console)
# ============================================================
print('\n=== SENSIBILIDADE (AUC-ROC no teste 2023-2024, Reg. Logistica otimizada) ===')

def auc_teste(df_tr_, df_te_, feats, imput='mediana'):
    df_tr_, df_te_ = df_tr_.copy(), df_te_.copy()
    cols_j = [c for c in feats if c not in FEATURES_ELENCO]
    ref = (df_tr_[cols_j].median() if imput == 'mediana' else df_tr_[cols_j].mean())
    for col in cols_j:
        df_tr_[col] = df_tr_[col].fillna(ref[col])
        df_te_[col] = df_te_[col].fillna(ref[col])
    sc = StandardScaler().fit(df_tr_[feats])
    m = clone(rl_otim)
    m.fit(sc.transform(df_tr_[feats]), df_tr_[TARGET].values)
    return roc_auc_score(df_te_[TARGET].values,
                         m.predict_proba(sc.transform(df_te_[feats]))[:, 1])

tr_raw = df_rot[df_rot['Temporada'] <= 2022]
te_raw = df_rot[df_rot['Temporada'] > 2022]
print('Config. original (mediana, janelas 3/5): %.3f' % auc_teste(tr_raw, te_raw, FEATURES))
print('Imputacao por MEDIA:                     %.3f' % auc_teste(tr_raw, te_raw, FEATURES, 'media'))
print('Apenas features de ELENCO:               %.3f' % auc_teste(tr_raw, te_raw, FEATURES_ELENCO))
fj = FEATURES_JANELA
print('Apenas features de DESEMPENHO:           %.3f' % auc_teste(tr_raw, te_raw, fj))

df_24, cols_24 = construir_base(janelas=(2, 4))
rot24 = df_24[df_24['Temporada'] < 2025]
print('Janelas 2/4 em vez de 3/5:               %.3f'
      % auc_teste(rot24[rot24['Temporada'] <= 2022], rot24[rot24['Temporada'] > 2022],
                  FEATURES_ELENCO + cols_24))

print('\nConcluido.')
