"""
gerar_app_real.py
-----------------
Lê o modelo treinado, computa todos os dados reais e gera
previsao_rebaixamento.html — arquivo único, auto-contido,
idêntico ao protótipo mas com dados reais.

Uso:
    python gerar_app_real.py
    # depois abra previsao_rebaixamento.html no navegador
"""

import os, sys, json, math
import numpy as np
import pandas as pd
import joblib

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from sklearn.metrics import (
    confusion_matrix, roc_curve, auc as sk_auc,
    precision_score, recall_score, f1_score, accuracy_score,
)
from sklearn.calibration import calibration_curve

from app.utils.processamento import (
    carregar_dados_excel, carregar_modelo,
    FEATURES, FEATURES_JANELA, FEATURES_ELENCO,
)

# ── Cores e UFs dos clubes ──────────────────────────────────────────────────
_COR = {
    "Flamengo":          "#E03A3E", "Palmeiras":     "#1B7A3D",
    "Botafogo":          "#2a2a2a", "São Paulo":     "#E03A3E",
    "Sao Paulo":         "#E03A3E", "Corinthians":   "#2a2a2a",
    "Atletico Mineiro":  "#2a2a2a", "Atlético Mineiro":"#2a2a2a",
    "Internacional":     "#E03A3E", "Cruzeiro":      "#1A3B8B",
    "Vasco da Gama":     "#2a2a2a", "Gremio":        "#1A6BB5",
    "Grêmio":            "#1A6BB5", "Fluminense":    "#7A1F2B",
    "Bahia":             "#1A6BB5", "Bragantino":    "#E03A3E",
    "Santos":            "#2a2a2a", "Fortaleza":     "#1A3B8B",
    "Vitoria":           "#E03A3E", "Vitória":       "#E03A3E",
    "Ceara":             "#2a2a2a", "Ceará":         "#2a2a2a",
    "Juventude":         "#1B7A3D", "Sport Recife":  "#E03A3E",
    "Sport":             "#E03A3E", "Mirassol":      "#1B7A3D",
    "América Mineiro":   "#1B7A3D", "America Mineiro":"#1B7A3D",
    "Cuiabá":            "#1B7A3D", "Coritiba":      "#1B7A3D",
    "Goiás":             "#1B7A3D", "Athletico Paranaense":"#E03A3E",
    "Criciúma":          "#F5A623", "Criciuma":      "#F5A623",
}
_UF = {
    "Flamengo":"RJ","Palmeiras":"SP","Botafogo":"RJ","São Paulo":"SP","Sao Paulo":"SP",
    "Corinthians":"SP","Atletico Mineiro":"MG","Internacional":"RS","Cruzeiro":"MG",
    "Vasco da Gama":"RJ","Gremio":"RS","Grêmio":"RS","Fluminense":"RJ","Bahia":"BA",
    "Bragantino":"SP","Santos":"SP","Fortaleza":"CE","Vitoria":"BA","Vitória":"BA",
    "Ceara":"CE","Ceará":"CE","Juventude":"RS","Sport Recife":"PE","Sport":"PE",
    "Mirassol":"SP","América Mineiro":"MG","America Mineiro":"MG","Cuiabá":"MT",
    "Coritiba":"PR","Goiás":"GO","Athletico Paranaense":"PR","Criciúma":"SC","Criciuma":"SC",
    "Atlético Mineiro":"MG",
}
_PROMOVIDOS_2025 = {"Mirassol", "Sport Recife", "Sport", "Ceara", "Ceará", "Santos"}


def gerar():
    print("Carregando modelo e dados...")
    modelo, scaler, mediana = carregar_modelo()
    df_full = carregar_dados_excel()

    # ── Conjunto de teste 2023-2024 ─────────────────────────────────────────
    df_te = df_full[(df_full["Temporada"] > 2022) & (df_full["Temporada"] < 2025)].copy()
    for col in FEATURES_JANELA:
        if col in df_te.columns:
            df_te[col] = df_te[col].fillna(mediana[col] if mediana is not None else 0)
        else:
            df_te[col] = mediana[col] if mediana is not None else 0

    X_te = scaler.transform(df_te[FEATURES])
    y_te = df_te["Status_bin"].values
    y_pred = modelo.predict(X_te)
    y_prob = modelo.predict_proba(X_te)[:, 1]

    # métricas
    acc   = float(accuracy_score(y_te, y_pred))
    prec  = float(precision_score(y_te, y_pred, zero_division=0))
    rec   = float(recall_score(y_te, y_pred, zero_division=0))
    f1    = float(f1_score(y_te, y_pred, zero_division=0))

    cm = confusion_matrix(y_te, y_pred)
    tn, fp, fn, tp = [int(x) for x in cm.ravel()]

    fpr_arr, tpr_arr, _ = roc_curve(y_te, y_prob)
    roc_auc = float(sk_auc(fpr_arr, tpr_arr))
    # amostra de 20 pontos para a curva ROC
    idx_roc = np.linspace(0, len(fpr_arr) - 1, 20, dtype=int)
    roc_pts = [[round(float(fpr_arr[i]), 4), round(float(tpr_arr[i]), 4)] for i in idx_roc]

    prob_true, prob_pred = calibration_curve(y_te, y_prob, n_bins=6, strategy="quantile")
    calib_pts = [[round(float(a), 4), round(float(b), 4)] for a, b in zip(prob_pred, prob_true)]

    # ── Coeficientes / odds ratios ──────────────────────────────────────────
    coefs = modelo.coef_[0]
    odds_rs = np.exp(coefs)
    feat_labels_raw = FEATURES
    feat_labels = [
        f.replace("_media_", " média ").replace("_", " ")
         .replace("Pts", "Pontos").replace("SG", "Saldo Gols")
         .replace("Gols Pro", "Gols Pró").replace("Gols Contra", "Gols Contra")
         .replace("Aproveitamento", "Aproveitamento").replace("Valor de Mercado Total", "Valor de mercado")
         .replace("Plantel", "Tamanho do plantel").replace("Estrangeiros", "Nº de estrangeiros")
        for f in feat_labels_raw
    ]
    idx_sort = np.argsort(np.abs(np.log(odds_rs + 1e-9)))[::-1]
    coefs_js = [
        {"feat": feat_labels[i], "coef": round(float(coefs[i]), 4), "or": round(float(odds_rs[i]), 4)}
        for i in idx_sort
    ]

    # ── Previsão 2025 ───────────────────────────────────────────────────────
    df_2025 = df_full[df_full["Temporada"] == 2025].copy()
    for col in FEATURES_JANELA:
        if col in df_2025.columns:
            df_2025[col] = df_2025[col].fillna(mediana[col] if mediana is not None else 0)
        else:
            df_2025[col] = mediana[col] if mediana is not None else 0

    X_2025 = scaler.transform(df_2025[FEATURES])
    probs_2025 = modelo.predict_proba(X_2025)[:, 1]

    # extrair features de desempenho para o display
    df_2025["prob"] = probs_2025
    clubes_2025_js = []
    for _, row in df_2025.iterrows():
        nome = str(row["Clube"])
        vm   = float(row.get("Valor de Mercado Total", 0) or 0)
        clubes_2025_js.append({
            "nome":      nome,
            "uf":        _UF.get(nome, "BR"),
            "cor":       _COR.get(nome, "#3a3a3a"),
            "vm":        round(vm, 1),
            "plantel":   int(row.get("Plantel", 0) or 0),
            "estr":      int(row.get("Estrangeiros", 0) or 0),
            "pts5":      round(float(row.get("Pts_media_5", 50) or 50), 1),
            "sg3":       round(float(row.get("SG_media_3", 0) or 0), 1),
            "apr":       round(float(row.get("Aproveitamento_media_5", 0.5) or 0.5), 3),
            "promovido": nome in _PROMOVIDOS_2025,
            "prob":      round(float(row["prob"]), 4),
        })

    # ── Scaler real para o simulador JS ────────────────────────────────────
    scaler_means  = scaler.mean_.tolist()
    scaler_scales = scaler.scale_.tolist()
    model_coef    = modelo.coef_[0].tolist()
    model_intercept = float(modelo.intercept_[0])
    # valores medianos das 12 features de janela (em unidade original)
    median_janelas = [float(mediana[col]) if mediana is not None and col in mediana else 0.0
                      for col in FEATURES_JANELA]

    # ── Dados históricos (amostra) ──────────────────────────────────────────
    df_hist = df_full[df_full["Temporada"].isin([2014, 2018, 2022])].copy()
    df_hist = df_hist.head(12)
    hist_sample = []
    for _, row in df_hist.iterrows():
        sit_raw = str(row.get("Situacao", row.get("Situação", ""))).strip().lower()
        if "rebaixado" in sit_raw:
            sit = "Rebaixado"
        elif "top" in sit_raw or "4" in sit_raw:
            sit = "Top 4"
        else:
            sit = "Série A"
        hist_sample.append({
            "clube": str(row["Clube"]),
            "temp":  int(row["Temporada"]),
            "plantel": int(row.get("Plantel", 0) or 0),
            "estr":    int(row.get("Estrangeiros", 0) or 0),
            "vm":      round(float(row.get("Valor de Mercado Total", 0) or 0), 2),
            "sit":     sit,
        })

    # ── VM médio por clube ──────────────────────────────────────────────────
    df_hist_all = df_full[df_full["Temporada"] < 2025]
    vm_medio = (df_hist_all.groupby("Clube")["Valor de Mercado Total"]
                            .mean()
                            .sort_values(ascending=False)
                            .head(20))
    vm_medio_js = [[str(k), round(float(v), 1)] for k, v in vm_medio.items()]

    # ── Descritiva 2024 ─────────────────────────────────────────────────────
    df_24 = df_full[df_full["Temporada"] == 2024].copy()
    num_cols = {
        "Plantel": "Tamanho do plantel",
        "Estrangeiros": "Nº de estrangeiros",
        "Valor de Mercado Total": "VM Total (M€)",
        "Pontos": "Pontos",
    }
    stats_2024 = []
    for col, label in num_cols.items():
        if col not in df_24.columns:
            continue
        s = df_24[col].dropna()
        if len(s) == 0:
            continue
        stats_2024.append({
            "v": label, "n": int(len(s)),
            "media": round(float(s.mean()), 2), "std": round(float(s.std()), 2),
            "min": round(float(s.min()), 1), "q1": round(float(s.quantile(0.25)), 2),
            "med": round(float(s.median()), 1), "q3": round(float(s.quantile(0.75)), 2),
            "max": round(float(s.max()), 1),
        })
    clubes_2024 = []
    for _, row in df_24.sort_values("Pontos", ascending=False).head(10).iterrows():
        clubes_2024.append({
            "clube":   str(row["Clube"]),
            "plantel": int(row.get("Plantel", 0) or 0),
            "estr":    int(row.get("Estrangeiros", 0) or 0),
            "vm":      round(float(row.get("Valor de Mercado Total", 0) or 0), 2),
            "pts":     int(row.get("Pontos", 0) or 0),
        })
    vm_med_24 = float(df_24["Valor de Mercado Total"].mean()) if "Valor de Mercado Total" in df_24.columns else 0
    pts_med_24 = float(df_24["Pontos"].mean()) if "Pontos" in df_24.columns else 0

    # ── Walk-forward AUC-ROC (notebooks) ────────────────────────────────────
    WF_AUC_CV  = 0.794
    WF_AUC_STD = 0.058

    # ── Comparação modelos (resultados reais notebooks 03-06) ───────────────
    modelos_comp = [
        {"nome":"LightGBM",           "sigla":"LGB","auc":0.700,"aucTeste":0.877,"acc":0.825,"f1":0.65,"escolhido":False,
         "nota":"Melhor AUC no teste, porém alta variância (±0.151)"},
        {"nome":"Random Forest",       "sigla":"RF", "auc":0.762,"aucTeste":0.844,"acc":0.800,"f1":0.60,"escolhido":False,
         "nota":"Bom AUC; menos interpretável"},
        {"nome":"Regressão Logística", "sigla":"LR", "auc":0.794,"aucTeste":roc_auc,"acc":acc,"f1":f1,"escolhido":True,
         "nota":"Melhor estabilidade walk-forward (±0.058) + interpretável"},
        {"nome":"XGBoost",             "sigla":"XGB","auc":0.659,"aucTeste":0.652,"acc":0.825,"f1":0.55,"escolhido":False,
         "nota":"Alta acurácia mas AUC baixo — viés para classe majoritária"},
    ]

    # ── Gerar data.js e model.js ────────────────────────────────────────────
    data_js = f"""
window.MODEL = {{
  algoritmo:"Regressão Logística",
  treino:"2014 – 2022",
  teste:"2023 – 2024",
  acuracia:{round(acc,4)},
  aucTeste:{round(roc_auc,4)},
  aucCV:{WF_AUC_CV},
  aucCVstd:{WF_AUC_STD},
  validacao:"Walk-forward (5 folds)",
  modelosTestados:["LR","RF","XGB","LGB"],
  registros:220,clubesUnicos:34,temporadas:11,rebaixamentos:44,
}};
window.MODELOS_COMP = {json.dumps(modelos_comp, ensure_ascii=False)};
window.FEATURES = {{
  elenco:[
    {{nome:"Tamanho do plantel",desc:"Nº de atletas no elenco"}},
    {{nome:"Nº de estrangeiros",desc:"Atletas não-brasileiros"}},
    {{nome:"Valor de mercado total",desc:"Soma do valor de mercado (M€)"}},
  ],
  janelas:[
    "Pontos · média 3 e 5 temporadas","Saldo de gols · média 3 e 5",
    "Gols marcados · média 3 e 5","Gols sofridos · média 3 e 5",
    "Vitórias · média 3 e 5","Aproveitamento (%) · média 3 e 5",
  ],
}};
window.COEFS = {json.dumps(coefs_js, ensure_ascii=False)};
window.CONFUSION = {{tn:{tn},fp:{fp},fn:{fn},tp:{tp}}};
window.ROC = {json.dumps(roc_pts)};
window.CALIB = {json.dumps(calib_pts)};
window.CLUBES_2025 = {json.dumps(clubes_2025_js, ensure_ascii=False)};
window.HIST_SAMPLE = {json.dumps(hist_sample, ensure_ascii=False)};
window.VM_MEDIO = {json.dumps(vm_medio_js, ensure_ascii=False)};
window.DESC_2024 = {{
  resumo:{{clubes:{len(df_24)},plantelMedio:{round(float(df_24['Plantel'].mean()) if 'Plantel' in df_24.columns else 0,1)},vmMedio:{round(vm_med_24,1)},ptsMedio:{round(pts_med_24,1)}}},
  stats:{json.dumps(stats_2024, ensure_ascii=False)},
  clubes:{json.dumps(clubes_2024, ensure_ascii=False)},
}};
"""

    model_js = f"""
/* Parâmetros reais do modelo treinado */
window._SCALER_MEAN  = {json.dumps([round(x,6) for x in scaler_means])};
window._SCALER_SCALE = {json.dumps([round(x,6) for x in scaler_scales])};
window._MODEL_COEF   = {json.dumps([round(x,6) for x in model_coef])};
window._MODEL_INTERCEPT = {round(model_intercept,6)};
window._MEDIAN_JANELAS  = {json.dumps([round(x,4) for x in median_janelas])};

/* Índices das features: [Plantel=0, Estrangeiros=1, VM=2, jan0..jan11=3..14] */

window.predictProb = function(c) {{
  // FEATURES order: Plantel, Estrangeiros, VM, Pts3, Pts5, SG3, SG5,
  //                 GPro3, GPro5, GContra3, GContra5, V3, V5, Apr3, Apr5
  var med = window._MEDIAN_JANELAS;
  var feats = [
    c.plantel   != null ? c.plantel   : window.SENS_BASE.plantel,
    c.estr      != null ? c.estr      : window.SENS_BASE.estr,
    c.vm        != null ? c.vm        : window.SENS_BASE.vm,
    c.pts3      != null ? c.pts3      : med[0],
    c.pts5      != null ? c.pts5      : med[1],
    c.sg3       != null ? c.sg3       : med[2],
    c.sg5       != null ? c.sg5       : med[3],
    c.gPro3     != null ? c.gPro3     : med[4],
    c.gPro5     != null ? c.gPro5     : med[5],
    c.gContra3  != null ? c.gContra3  : med[6],
    c.gContra5  != null ? c.gContra5  : med[7],
    c.vit3      != null ? c.vit3      : med[8],
    c.vit5      != null ? c.vit5      : med[9],
    c.apr3      != null ? c.apr3      : med[10],
    c.apr5      != null ? c.apr5      : med[11],
  ];
  var logit = window._MODEL_INTERCEPT;
  for (var i = 0; i < 15; i++) {{
    logit += window._MODEL_COEF[i] * (feats[i] - window._SCALER_MEAN[i]) / window._SCALER_SCALE[i];
  }}
  return 1 / (1 + Math.exp(-logit));
}};

/* predictSimple: recebe todos os inputs do simulador (apr em %, converte para decimal) */
window.predictSimple = function(plantel, estr, vm, pts, sg, gPro, gContra, vit, apr) {{
  var aprDec = (apr != null) ? apr / 100 : null;
  return window.predictProb({{
    plantel: plantel, estr: estr, vm: vm,
    pts3: pts,  pts5: pts,
    sg3: sg,    sg5: sg,
    gPro3: gPro,    gPro5: gPro,
    gContra3: gContra, gContra5: gContra,
    vit3: vit,  vit5: vit,
    apr3: aprDec, apr5: aprDec,
  }});
}};

window.riskBand = function(p) {{
  if (p >= 0.50) return {{label:"Risco alto",   key:"alto",  cor:"var(--red)"}};
  if (p >= 0.30) return {{label:"Risco moderado",key:"medio",cor:"var(--amber)"}};
  if (p >= 0.15) return {{label:"Atenção",       key:"baixo",cor:"var(--lime)"}};
  return {{label:"Risco baixo", key:"seguro", cor:"var(--green)"}};
}};

window.ranking2025 = function() {{
  return window.CLUBES_2025.slice().sort(function(a,b){{return b.prob - a.prob;}});
}};

window.SENS_BASE = {{plantel:28, estr:4, vm:85}};

window.sensCurve = function(varName, range) {{
  var pts = [];
  for (var i = 0; i <= 60; i++) {{
    var x = range[0] + (range[1] - range[0]) * (i / 60);
    var c = {{plantel:window.SENS_BASE.plantel, estr:window.SENS_BASE.estr, vm:window.SENS_BASE.vm}};
    c[varName] = x;
    pts.push([x, window.predictProb(c)]);
  }}
  return pts;
}};

window.fmtPct = function(p, d) {{
  d = d != null ? d : 1;
  return (p * 100).toFixed(d).replace(".", ",") + "%";
}};
window.fmtNum = function(n, d) {{
  d = d != null ? d : 1;
  return Number(n).toLocaleString("pt-BR", {{minimumFractionDigits:d, maximumFractionDigits:d}});
}};
"""

    # ── Ler arquivos JSX ────────────────────────────────────────────────────
    jsxdir = os.path.join(ROOT_DIR, "prototipo", "app")
    def read_jsx(name):
        with open(os.path.join(jsxdir, name), encoding="utf-8") as f:
            return f.read()

    ui_jsx      = read_jsx("ui.jsx")
    charts_jsx  = read_jsx("charts.jsx")
    screens1    = read_jsx("screens1.jsx")
    screens2    = read_jsx("screens2.jsx")
    main_jsx    = read_jsx("main.jsx")

    # ── CSS do protótipo ────────────────────────────────────────────────────
    css = """
:root{
  --bg:#0c0f12;--surface:#141a1f;--surface-2:#1a212a;--surface-3:#232d38;
  --border:rgba(255,255,255,.08);--border-2:rgba(255,255,255,.14);
  --text:#eef2f5;--muted:#8b98a4;--faint:#5e6b77;
  --green:#33c46a;--lime:#a8d94b;--blue:#4f9cf5;--violet:#9b7cf0;
  --red:#f0524b;--amber:#e3a93b;
  --grid:rgba(255,255,255,.06);--bar-dim:rgba(120,185,150,.32);
  --serif:'Source Serif 4',Georgia,serif;
  --sans:'IBM Plex Sans',system-ui,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,monospace;
  --shadow:0 1px 0 rgba(255,255,255,.03) inset,0 12px 32px -16px rgba(0,0,0,.7);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--sans);font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased;background-image:radial-gradient(1200px 600px at 80% -10%,rgba(51,196,106,.05),transparent 60%);}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
em{font-style:normal;color:var(--faint);font-size:.82em;font-family:var(--mono)}
.app{display:block;min-height:100vh}
.main{min-width:0;padding:40px 52px 80px;max-width:1180px;margin-left:278px;transition:margin-left .25s}
.app-wide .main{margin-left:0}
@media(max-width:1100px){.main{padding:28px 26px 60px}}
.sidebar{background:var(--surface);border-right:1px solid var(--border);padding:22px 18px;display:flex;flex-direction:column;gap:18px;position:fixed;top:0;left:0;width:278px;height:100vh;overflow-y:auto;z-index:20;transition:transform .25s}
.sb-closed{transform:translateX(-278px)}
.sb-brand{display:flex;align-items:center;gap:11px}
.sb-logo{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;background:linear-gradient(150deg,#1f7a44,#0f3d23);color:#bff5cf;flex:none;box-shadow:0 0 0 1px rgba(51,196,106,.3),0 6px 14px -6px rgba(51,196,106,.5)}
.sb-title{font-family:var(--serif);font-weight:700;font-size:17px;letter-spacing:-.01em}
.sb-sub{font-size:11.5px;color:var(--muted)}
.sb-close{margin-left:auto;background:none;border:none;color:var(--faint);cursor:pointer;padding:4px;border-radius:8px}
.sb-close:hover{background:var(--surface-2);color:var(--text)}
.sb-open{position:fixed;top:16px;left:16px;z-index:30;background:var(--surface-2);border:1px solid var(--border);color:var(--text);width:40px;height:40px;border-radius:10px;cursor:pointer;display:grid;place-items:center}
.sb-navlabel{font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;color:var(--faint);margin:2px 0 8px 4px;font-weight:600}
.sb-nav{display:flex;flex-direction:column;gap:2px}
.nav-item{display:flex;align-items:center;gap:11px;width:100%;text-align:left;background:none;border:none;color:var(--muted);font-family:var(--sans);font-size:14px;padding:9px 11px;border-radius:10px;cursor:pointer;position:relative;transition:.15s}
.nav-item:hover{background:var(--surface-2);color:var(--text)}
.nav-dot{width:6px;height:6px;border-radius:50%;background:transparent;flex:none}
.nav-label{flex:1}
.nav-new{font-size:9px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#0c0f12;background:var(--lime);padding:2px 6px;border-radius:5px}
.nav-on{background:linear-gradient(90deg,rgba(51,196,106,.14),rgba(51,196,106,.03));color:var(--text);font-weight:600}
.nav-on .nav-dot{background:var(--green);box-shadow:0 0 8px var(--green)}
.model-mini{background:var(--surface-2);border:1px solid var(--border);border-radius:14px;padding:14px;margin-top:auto}
.mm-title{font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);font-weight:600;margin-bottom:10px}
.mm-row{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:12.5px;padding:6px 0;border-bottom:1px solid var(--border);color:var(--muted)}
.mm-row:last-of-type{border-bottom:none}
.mm-row b{color:var(--text);font-weight:600;font-family:var(--mono);font-size:11.5px;text-align:right}
.mm-feat{margin-top:10px;border-top:1px dashed var(--border);padding-top:10px}
.mm-feat-h{font-size:11.5px;color:var(--muted);display:flex;align-items:center;gap:6px;margin-bottom:8px;font-weight:600}
.mm-feat-tags{display:flex;flex-wrap:wrap;gap:5px}
.mm-feat-tags span{display:inline-flex;align-items:center;gap:4px;font-size:10.5px;background:var(--surface-3);color:var(--muted);padding:3px 7px;border-radius:6px}
.sb-foot{font-size:10.5px;color:var(--faint);line-height:1.5;padding:0 4px}
.hero{position:relative;overflow:hidden;border-radius:18px;padding:30px 32px;margin-bottom:24px;background:linear-gradient(120deg,#0f3826 0%,#123e57 55%,#0d2540 100%);border:1px solid rgba(255,255,255,.07)}
.hero-compact{padding:22px 28px}
.hero-lines{position:absolute;inset:0;opacity:.5;pointer-events:none;background:repeating-linear-gradient(90deg,transparent 0 78px,rgba(255,255,255,.04) 78px 79px),radial-gradient(420px 220px at 88% 120%,rgba(51,196,106,.22),transparent 70%)}
.hero-body{position:relative}
.hero-tag{display:inline-flex;align-items:center;gap:7px;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:#bdebcf;background:rgba(0,0,0,.22);padding:5px 11px;border-radius:20px;border:1px solid rgba(255,255,255,.1);font-weight:600;margin-bottom:14px}
.hero h1{font-family:var(--serif);font-weight:700;font-size:30px;line-height:1.12;margin:0 0 8px;letter-spacing:-.015em}
.hero-compact h1{font-size:24px}
.hero-em{color:#9fd9ff;font-weight:600}
.hero p{margin:0;color:#c5d6dd;font-size:13.5px}
.sec-title{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin:30px 0 16px}
.sec-kicker{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--green);font-weight:600;margin-bottom:5px}
.sec-title h2{font-family:var(--serif);font-weight:600;font-size:21px;margin:0;letter-spacing:-.01em}
.card{background:var(--surface);border:1px solid var(--border);border-radius:16px;box-shadow:var(--shadow)}
.card-pad{padding:20px 22px}
.card-title{display:flex;align-items:center;gap:8px;font-weight:600;font-size:13.5px;color:var(--muted);margin-bottom:16px;letter-spacing:.01em}
.card-title>svg{color:var(--green)}
.callout{display:flex;gap:12px;padding:14px 18px;border-radius:13px;font-size:13.5px;line-height:1.55;background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--blue);margin:14px 0;color:var(--muted)}
.callout b,.callout strong{color:var(--text);font-weight:600}
.callout-ic{flex:none;margin-top:2px;color:var(--blue)}
.callout-info{border-left-color:var(--blue)}.callout-info .callout-ic{color:var(--blue)}
.callout-warn{border-left-color:var(--amber);background:linear-gradient(90deg,rgba(227,169,59,.07),transparent)}.callout-warn .callout-ic{color:var(--amber)}
.callout-muted{border-left-color:var(--faint)}.callout-muted .callout-ic{color:var(--faint)}
.metric-row,.rank-kpis,.hist-kpis,.sens-kpis,.desc-kpis{display:grid;gap:14px;margin:6px 0 4px}
.rank-kpis,.hist-kpis,.desc-kpis{grid-template-columns:repeat(4,1fr)}
.sens-kpis{grid-template-columns:repeat(3,1fr)}
.metric-row{grid-template-columns:repeat(6,1fr)}
@media(max-width:1000px){.metric-row{grid-template-columns:repeat(3,1fr)}.rank-kpis,.hist-kpis,.desc-kpis{grid-template-columns:repeat(2,1fr)}}
.stat{background:var(--surface);border:1px solid var(--border);border-radius:13px;padding:15px 16px}
.stat-label{font-size:11.5px;color:var(--muted);margin-bottom:7px;font-weight:500}
.stat-value{font-family:var(--serif);font-weight:700;font-size:26px;letter-spacing:-.02em;line-height:1}
.stat-unit{font-size:13px;color:var(--muted);font-weight:500;margin-left:3px;font-family:var(--sans)}
.stat-sub{font-size:11px;color:var(--faint);margin-top:6px}
.tabs{display:flex;gap:4px;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:5px;margin:20px 0 16px;flex-wrap:wrap}
.tab{display:inline-flex;align-items:center;gap:7px;border:none;background:none;cursor:pointer;color:var(--muted);font-family:var(--sans);font-size:13px;font-weight:500;padding:8px 14px;border-radius:8px;transition:.15s}
.tab:hover{color:var(--text)}
.tab-on{background:var(--surface-3);color:var(--text);font-weight:600;box-shadow:0 0 0 1px var(--border)}
.badge{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:600;padding:3px 9px;border-radius:20px;line-height:1.3}
.badge-neutral{background:var(--surface-3);color:var(--muted)}
.badge-ok{background:rgba(51,196,106,.16);color:var(--green)}
.badge-danger{background:rgba(240,82,75,.16);color:var(--red)}
.badge-warn{background:rgba(227,169,59,.16);color:var(--amber)}
.crest{display:inline-grid;place-items:center;border-radius:50%;color:#fff;font-weight:700;font-family:var(--mono);flex:none;box-shadow:0 0 0 1px rgba(255,255,255,.18),0 2px 6px rgba(0,0,0,.4);letter-spacing:-.02em}
.probbar{position:relative;width:100%;background:var(--surface-3);border-radius:20px;overflow:hidden}
.probbar-zone{position:absolute;right:0;top:0;bottom:0;width:50%;background:repeating-linear-gradient(45deg,rgba(240,82,75,.06) 0 6px,transparent 6px 12px)}
.probbar-fill{position:absolute;left:0;top:0;bottom:0;border-radius:20px;transition:width .4s}
.field{margin-bottom:18px}
.field-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:9px}
.field-head label{font-size:13px;font-weight:500;color:var(--text);display:inline-flex;align-items:center;gap:7px}
.field-val{font-family:var(--mono);font-size:14px;font-weight:600;color:var(--green)}
.text-input{width:100%;background:var(--surface-2);border:1px solid var(--border);border-radius:10px;padding:11px 13px;color:var(--text);font-family:var(--sans);font-size:14px}
.text-input:focus{outline:none;border-color:var(--green)}
input[type=range]{-webkit-appearance:none;width:100%;height:6px;border-radius:6px;background:linear-gradient(90deg,var(--green) var(--pct),var(--surface-3) var(--pct));cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:18px;height:18px;border-radius:50%;background:#fff;border:3px solid var(--green);box-shadow:0 2px 6px rgba(0,0,0,.4);cursor:pointer}
.field-scale{display:flex;justify-content:space-between;font-size:11px;color:var(--faint);margin-top:7px;font-family:var(--mono)}
.field-hint{font-size:11.5px;color:var(--faint);margin-top:6px}
.sim-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:900px){.sim-grid{grid-template-columns:1fr}}
.result-card{background:linear-gradient(180deg,var(--surface),var(--surface-2))}
.result-gauge{display:flex;flex-direction:column;align-items:center;gap:6px;padding:6px 0 14px}
.gauge-val{font-family:var(--serif);font-weight:700;font-size:30px}
.gauge-lbl{font-size:11px;fill:var(--muted);font-family:var(--sans)}
.result-club{display:inline-flex;align-items:center;gap:8px;font-weight:600;font-size:14px}
.result-verdict{display:flex;flex-direction:column;gap:8px;align-items:center;text-align:center;padding:14px;border:1px solid var(--border);border-left-width:3px;border-radius:12px;background:var(--surface);font-size:13px;color:var(--muted)}
.result-verdict b{color:var(--text)}
.result-factors{margin-top:16px;display:flex;flex-direction:column;gap:9px}
.rf{display:flex;align-items:center;gap:10px;font-size:13px}
.rf-l{flex:1;color:var(--muted)}
.rf-tag{display:inline-flex;align-items:center;gap:4px;font-size:11.5px;font-weight:600}
.rank-card{overflow:hidden}
.rank-head,.rank-row{display:grid;grid-template-columns:44px minmax(150px,2.7fr) minmax(110px,3fr) 66px 72px;align-items:center;gap:12px;padding:11px 18px}
.rank-head{font-size:11px;letter-spacing:.04em;text-transform:uppercase;color:var(--faint);font-weight:600;border-bottom:1px solid var(--border)}
.rank-row{border-bottom:1px solid var(--border);cursor:pointer;transition:.12s}
.rank-row:hover{background:var(--surface-2)}
.rank-zone{background:linear-gradient(90deg,rgba(240,82,75,.08),transparent 70%)}
.rank-zone:hover{background:linear-gradient(90deg,rgba(240,82,75,.13),transparent 70%)}
.rank-sel{box-shadow:inset 3px 0 0 var(--green)}
.rk-pos{display:flex;justify-content:center}
.rk-num{font-family:var(--serif);font-weight:700;font-size:18px;color:var(--muted)}
.rk-club{display:flex;align-items:center;gap:10px;min-width:0}
.rk-name{font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rk-uf{font-size:10.5px;color:var(--faint);font-family:var(--mono);margin-left:auto;padding-left:6px;flex:none}
.rk-pct{font-family:var(--mono);font-weight:600;font-size:14px;text-align:right}
.rk-vm{font-family:var(--mono);font-size:13px;color:var(--muted);text-align:right}
.rank-corte{display:flex;align-items:center;gap:7px;justify-content:center;font-size:11.5px;color:var(--faint);padding:11px;background:var(--surface-2);border-top:1px dashed rgba(240,82,75,.3)}
.chart-trio{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:6px}
@media(max-width:980px){.chart-trio{grid-template-columns:1fr}}
.mini-note{font-size:11.5px;color:var(--faint);margin-top:10px;line-height:1.5}
.confusion{display:grid;grid-template-columns:auto 1fr 1fr;grid-template-rows:auto 1fr 1fr;gap:6px}
.cf-corner{}.cf-coltop{font-size:10.5px;color:var(--muted);text-align:center;padding-bottom:2px;font-weight:600}
.cf-rowside{font-size:10.5px;color:var(--muted);writing-mode:vertical-rl;transform:rotate(180deg);text-align:center;font-weight:600;align-self:center}
.cf-cell{border-radius:11px;padding:14px 8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;min-height:78px}
.cf-good{background:rgba(51,196,106,.18);border:1px solid rgba(51,196,106,.3)}
.cf-bad{background:rgba(240,82,75,.18);border:1px solid rgba(240,82,75,.3)}
.cf-num{font-family:var(--serif);font-weight:700;font-size:28px}
.cf-lbl{font-size:10px;color:var(--muted);text-align:center}
.roc,.linechart,.vbars{width:100%;height:auto;display:block}
.ax{font-size:10px;fill:var(--faint);font-family:var(--mono)}
.ax-val{font-size:10px;fill:var(--muted);font-family:var(--mono);font-weight:600}
.ax-cat{font-size:10px;fill:var(--muted);font-family:var(--sans)}
.ax-title{font-size:10.5px;fill:var(--muted);font-family:var(--sans)}
.roc-auc{font-size:13px;fill:var(--green);font-weight:700;font-family:var(--mono)}
.comp-table{width:100%}
.comp-head,.comp-row{display:grid;grid-template-columns:1.9fr 1fr .9fr .7fr .6fr 2fr;gap:12px;align-items:center;padding:12px 20px}
.comp-head{font-size:11px;letter-spacing:.03em;text-transform:uppercase;color:var(--faint);font-weight:600;border-bottom:1px solid var(--border)}
.comp-row{border-bottom:1px solid var(--border);font-size:13px}
.comp-row:last-child{border-bottom:none}
.comp-on{background:linear-gradient(90deg,rgba(51,196,106,.1),transparent 60%)}
.comp-name{display:flex;align-items:center;gap:7px;font-weight:600}
.comp-check{color:var(--green)}
.comp-note{font-size:12px;color:var(--muted)}
.or-chart{display:flex;flex-direction:column;gap:9px}
.or-row{display:grid;grid-template-columns:220px 1fr 54px;gap:14px;align-items:center}
.or-feat{font-size:12.5px;color:var(--muted);text-align:right}
.or-track{position:relative;height:22px}
.or-axis{position:absolute;left:50%;top:-3px;bottom:-3px;width:1px;background:var(--border-2)}
.or-bar{position:absolute;top:4px;bottom:4px;border-radius:4px;opacity:.85}
.or-val{font-size:13px;font-weight:600;text-align:left}
.or-axislabels{display:flex;justify-content:space-between;font-size:10.5px;color:var(--faint);padding:8px 54px 0 220px;font-family:var(--mono)}
.filters{margin-bottom:18px}
.filter-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr .9fr;gap:16px}
.filter-col label{display:block;font-size:11.5px;color:var(--muted);margin-bottom:8px;font-weight:500}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:500;padding:6px 11px;border-radius:8px;background:var(--surface-2);border:1px solid var(--border);color:var(--muted);cursor:pointer;transition:.15s}
.chip-on{background:rgba(240,82,75,.16);border-color:rgba(240,82,75,.35);color:#ff8a84}
.dt-grid{grid-template-columns:40px 1.6fr 1fr .8fr .7fr 1fr 1.1fr}
.clube-grid{grid-template-columns:2fr 1fr .8fr 1fr 1fr}
.st-grid{grid-template-columns:1.7fr .6fr 1fr 1fr .8fr .9fr 1fr .9fr .8fr}
.dt-head,.st-head{display:grid;gap:12px;padding:12px 20px;font-size:11px;letter-spacing:.03em;text-transform:uppercase;color:var(--faint);font-weight:600;border-bottom:1px solid var(--border)}
.dt-row,.st-row{display:grid;gap:12px;padding:12px 20px;font-size:13.5px;border-bottom:1px solid var(--border);align-items:center}
.dt-row:last-child,.st-row:last-child{border-bottom:none}
.dt-row:hover,.st-row:hover{background:var(--surface-2)}
.dt-mut{color:var(--faint)}
.dt-club{display:flex;align-items:center;gap:9px;font-weight:500}
.st-name{font-weight:500}
.st-pts{color:var(--green);font-weight:600}
.dt-footer{display:flex;justify-content:space-between;align-items:center;padding:13px 20px;font-size:12px;color:var(--faint)}
.dist-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.dist-cell{text-align:center;padding:14px;background:var(--surface-2);border:1px solid var(--border);border-radius:13px}
.dist-big{font-family:var(--serif);font-weight:700;font-size:38px;line-height:1}
.dist-lbl{font-size:13px;font-weight:600;margin:6px 0 10px}
.dist-bar{height:7px;background:var(--surface-3);border-radius:6px;overflow:hidden;margin-bottom:7px}
.dist-bar>div{height:100%;border-radius:6px}
.jan-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.jan-cell{display:flex;align-items:center;gap:9px;font-size:13px;color:var(--muted);background:var(--surface-2);border:1px solid var(--border);border-radius:10px;padding:12px 14px}
.sens-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
@media(max-width:980px){.sens-grid{grid-template-columns:1fr}}
.desc-season{margin:14px 0 18px}
.desc-season label{display:block;font-size:11.5px;color:var(--muted);margin-bottom:8px;font-weight:500}
.select{display:flex;align-items:center;justify-content:space-between;background:var(--surface-2);border:1px solid var(--border);border-radius:10px;padding:11px 13px;font-size:13.5px;color:var(--text);cursor:pointer}
.select>svg{color:var(--muted)}
.select-sm{max-width:220px}
.boxplots{display:flex;flex-direction:column;gap:18px;padding:6px 0}
.boxrow{display:grid;grid-template-columns:160px 1fr 90px;gap:14px;align-items:center}
.box-name{font-size:12.5px;color:var(--muted);text-align:right}
.box-track{position:relative;height:30px}
.box-whisker{position:absolute;top:50%;height:2px;transform:translateY(-50%);opacity:.5;border-radius:2px}
.box-iqr{position:absolute;top:6px;bottom:6px;border-radius:5px;opacity:.32}
.box-med{position:absolute;top:4px;bottom:4px;width:3px;background:#fff;border-radius:2px}
.box-cap{position:absolute;top:10px;bottom:10px;width:2px;background:rgba(255,255,255,.55)}
.box-range{font-family:var(--mono);font-size:11.5px;color:var(--faint);text-align:left}
.screen{animation:fade .4s ease}
@keyframes fade{from{transform:translateY(8px)}to{transform:none}}
"""

    # ── Montar HTML final ────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Previsão de Rebaixamento — Brasileirão Série A 2025</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div id="root"></div>

<script src="https://unpkg.com/react@18.3.1/umd/react.development.js" crossorigin="anonymous"></script>
<script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" crossorigin="anonymous"></script>
<script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" crossorigin="anonymous"></script>

<!-- DADOS REAIS -->
<script>{data_js}</script>
<!-- MODELO REAL -->
<script>{model_js}</script>

<!-- COMPONENTES UI -->
<script type="text/babel">{ui_jsx}</script>
<script type="text/babel">{charts_jsx}</script>
<script type="text/babel">{screens1}</script>
<script type="text/babel">{screens2}</script>
<script type="text/babel">{main_jsx}</script>
</body>
</html>"""

    out_path = os.path.join(ROOT_DIR, "previsao_rebaixamento.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"\nGerado: previsao_rebaixamento.html ({size_kb:.0f} KB)")
    print("   Abra no navegador para ver o app completo.")
    return out_path


if __name__ == "__main__":
    gerar()
