import streamlit as st


# ── design tokens ────────────────────────────────────────────────────────────
GREEN  = "#33c46a"
RED    = "#f0524b"
AMBER  = "#e3a93b"
BLUE   = "#4f9cf5"
VIOLET = "#9b7cf0"
LIME   = "#a8d94b"
MUTED  = "#8b98a4"
FAINT  = "#5e6b77"
BG     = "#0c0f12"
SURF   = "#141a1f"
SURF2  = "#1a212a"
SURF3  = "#232d38"
BORDER = "rgba(255,255,255,.08)"
BORDER2= "rgba(255,255,255,.14)"
TEXT   = "#eef2f5"

# plotly template base
PLOTLY_LAYOUT = dict(
    paper_bgcolor=SURF,
    plot_bgcolor =SURF,
    font=dict(color=MUTED, family="IBM Plex Sans, sans-serif", size=12),
    xaxis=dict(gridcolor="rgba(255,255,255,.06)", zerolinecolor="rgba(255,255,255,.1)", color=MUTED),
    yaxis=dict(gridcolor="rgba(255,255,255,.06)", zerolinecolor="rgba(255,255,255,.1)", color=MUTED),
    margin=dict(l=16, r=16, t=40, b=16),
)


def apply_custom_css():
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* ── base ── */
html, body, [class*="css"] {
  font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
  background-color: #0c0f12 !important;
  color: #eef2f5 !important;
}
.main .block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1140px; }

/* ── hide chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── hero banner ── */
.hero {
  position: relative; overflow: hidden;
  border-radius: 16px;
  padding: 28px 32px 32px;
  margin-bottom: 22px;
  background: linear-gradient(120deg,#0f3826 0%,#123e57 55%,#0d2540 100%);
  border: 1px solid rgba(255,255,255,.07);
}
.hero::before {
  content: '';
  position: absolute; inset: 0;
  opacity: .5; pointer-events: none;
  background:
    repeating-linear-gradient(90deg,transparent 0 78px,rgba(255,255,255,.04) 78px 79px),
    radial-gradient(420px 220px at 88% 120%,rgba(51,196,106,.22),transparent 70%);
}
.hero-tag {
  display: inline-block;
  font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase;
  color: #bdebcf; background: rgba(0,0,0,.22);
  padding: 5px 12px; border-radius: 20px;
  border: 1px solid rgba(255,255,255,.1);
  font-weight: 600; margin-bottom: 12px;
}
.hero h1 {
  font-family: 'Source Serif 4', Georgia, serif !important;
  font-weight: 700; font-size: 1.85rem; line-height: 1.2;
  margin: 0 0 7px; color: #fff; letter-spacing: -.01em;
}
.hero-em { color: #9fd9ff; }
.hero p { margin: 0; color: #c5d6dd; font-size: 13px; }

/* ── section title ── */
.sec-kicker {
  font-size: 10px; letter-spacing: .14em; text-transform: uppercase;
  color: #33c46a; font-weight: 600; margin-bottom: 4px;
}
.sec-h2 {
  font-family: 'Source Serif 4', Georgia, serif !important;
  font-weight: 600; font-size: 1.2rem; margin: 0 0 14px;
  color: #eef2f5; letter-spacing: -.01em;
}

/* ── callout ── */
.callout {
  display: flex; gap: 12px;
  padding: 13px 16px; border-radius: 12px;
  background: #141a1f; border: 1px solid rgba(255,255,255,.08);
  border-left: 3px solid #4f9cf5;
  font-size: 13.5px; line-height: 1.6; color: #8b98a4;
  margin: 12px 0 18px;
}
.callout b, .callout strong { color: #eef2f5; font-weight: 600; }
.callout-warn  { border-left-color: #e3a93b; background: linear-gradient(90deg,rgba(227,169,59,.07),transparent); }
.callout-muted { border-left-color: #5e6b77; }
.callout-green { border-left-color: #33c46a; }

/* ── stat / kpi card ── */
.stat-card {
  background: #141a1f; border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px; padding: 16px 18px;
  box-shadow: 0 12px 32px -16px rgba(0,0,0,.7);
}
.stat-label {
  font-size: 11px; color: #8b98a4; font-weight: 500;
  text-transform: uppercase; letter-spacing: .04em; margin-bottom: 6px;
}
.stat-value {
  font-family: 'Source Serif 4', Georgia, serif !important;
  font-weight: 700; font-size: 1.7rem; line-height: 1; color: #eef2f5;
}
.stat-unit { font-size: 13px; color: #8b98a4; font-weight: 500; margin-left: 3px; font-family: 'IBM Plex Sans', sans-serif !important; }
.stat-sub  { font-size: 11px; color: #5e6b77; margin-top: 6px; }

/* ── badge ── */
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 20px; line-height: 1.3;
}
.badge-ok      { background: rgba(51,196,106,.16);  color: #33c46a; }
.badge-danger  { background: rgba(240,82,75,.16);   color: #f0524b; }
.badge-warn    { background: rgba(227,169,59,.16);  color: #e3a93b; }
.badge-neutral { background: rgba(255,255,255,.08); color: #8b98a4; }
.badge-lime    { background: rgba(168,217,75,.16);  color: #a8d94b; }

/* ── prob bar ── */
.probbar-wrap { position: relative; width: 100%; background: #232d38; border-radius: 20px; overflow: hidden; height: 10px; }
.probbar-fill { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 20px; }

/* ── ranking table ── */
.rank-table { width: 100%; border-collapse: collapse; }
.rank-head th {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px; font-weight: 600;
  letter-spacing: .04em; text-transform: uppercase; color: #5e6b77;
  padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,.08);
  text-align: left;
}
.rank-row td {
  padding: 11px 14px; border-bottom: 1px solid rgba(255,255,255,.06);
  font-size: 13.5px; vertical-align: middle;
}
.rank-row:hover td { background: #1a212a; }
.rank-zone td { background: rgba(240,82,75,.06); }
.rank-zone:hover td { background: rgba(240,82,75,.11); }
.rk-num { font-family: 'Source Serif 4', Georgia, serif; font-weight: 700; font-size: 18px; color: #5e6b77; }
.rk-num-zone { color: #f0524b; }
.rk-name { font-weight: 600; font-size: 14px; }
.rk-mono { font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 13.5px; }
.rk-muted { font-family: 'IBM Plex Mono', monospace; font-size: 12.5px; color: #8b98a4; }

/* ── crest (initials disk) ── */
.crest {
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 50%; color: #fff; font-weight: 700;
  font-family: 'IBM Plex Mono', monospace;
  box-shadow: 0 0 0 1px rgba(255,255,255,.18), 0 2px 6px rgba(0,0,0,.4);
  flex: none; letter-spacing: -.02em;
}

/* ── comparison table (model comparison) ── */
.comp-table { width: 100%; border-collapse: collapse; }
.comp-head th {
  font-size: 10px; letter-spacing: .04em; text-transform: uppercase;
  color: #5e6b77; font-weight: 600;
  padding: 10px 16px; border-bottom: 1px solid rgba(255,255,255,.08);
  text-align: left;
}
.comp-row td {
  padding: 11px 16px; border-bottom: 1px solid rgba(255,255,255,.06);
  font-size: 13px;
}
.comp-row-on td { background: linear-gradient(90deg,rgba(51,196,106,.1),transparent 60%); }
.comp-mono { font-family: 'IBM Plex Mono', monospace; }
.comp-note { color: #8b98a4; font-size: 12px; }

/* ── confusion matrix ── */
.cf-grid { display: grid; grid-template-columns: 90px 1fr 1fr; grid-template-rows: 28px 1fr 1fr; gap: 6px; }
.cf-corner {}
.cf-coltop { font-size: 10.5px; color: #8b98a4; text-align: center; padding-bottom: 2px; font-weight: 600; align-self: end; }
.cf-rowside { font-size: 10.5px; color: #8b98a4; text-align: center; font-weight: 600; writing-mode: vertical-rl; transform: rotate(180deg); align-self: center; }
.cf-cell { border-radius: 11px; padding: 16px 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 3px; min-height: 80px; }
.cf-good { background: rgba(51,196,106,.18); border: 1px solid rgba(51,196,106,.3); }
.cf-bad  { background: rgba(240,82,75,.18);  border: 1px solid rgba(240,82,75,.3);  }
.cf-num  { font-family: 'Source Serif 4', Georgia, serif; font-weight: 700; font-size: 2rem; }
.cf-lbl  { font-size: 10.5px; color: #8b98a4; text-align: center; }

/* ── odds ratio bars ── */
.or-row  { display: grid; grid-template-columns: 210px 1fr 60px; gap: 12px; align-items: center; margin-bottom: 10px; }
.or-feat { font-size: 12.5px; color: #8b98a4; text-align: right; }
.or-track { position: relative; height: 22px; }
.or-axis  { position: absolute; left: 50%; top: -2px; bottom: -2px; width: 1px; background: rgba(255,255,255,.14); }
.or-bar   { position: absolute; top: 4px; bottom: 4px; border-radius: 4px; opacity: .85; }
.or-val   { font-family: 'IBM Plex Mono', monospace; font-size: 13px; font-weight: 600; }
.or-labels { display: flex; justify-content: space-between; font-size: 10.5px; color: #5e6b77; padding: 4px 60px 0 210px; font-family: 'IBM Plex Mono', monospace; }

/* ── tabs (Streamlit native override) ── */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px; background: #141a1f;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 11px; padding: 5px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px; color: #8b98a4;
  font-weight: 500; font-size: 13px;
  background: transparent !important;
}
.stTabs [aria-selected="true"] {
  background: #232d38 !important;
  color: #eef2f5 !important;
  font-weight: 600 !important;
  box-shadow: 0 0 0 1px rgba(255,255,255,.08) !important;
}

/* ── sidebar styling ── */
[data-testid="stSidebar"] {
  background: #141a1f !important;
  border-right: 1px solid rgba(255,255,255,.08) !important;
}
[data-testid="stSidebar"] * { color: #8b98a4; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #eef2f5; }
.sb-label {
  font-size: 10px; letter-spacing: .13em; text-transform: uppercase;
  color: #5e6b77; font-weight: 600; margin: 14px 0 6px 4px;
}
.mm-card {
  background: #1a212a; border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px; padding: 14px; margin-top: 8px;
}
.mm-row {
  display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;
  font-size: 12px; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,.06);
  color: #8b98a4;
}
.mm-row:last-child { border-bottom: none; }
.mm-row b { color: #eef2f5; font-weight: 600; font-family: 'IBM Plex Mono', monospace; font-size: 11.5px; text-align: right; }
.mm-feat { margin-top: 10px; border-top: 1px dashed rgba(255,255,255,.08); padding-top: 10px; }
.mm-tag  { display: inline-block; font-size: 10.5px; background: #232d38; color: #8b98a4; padding: 3px 7px; border-radius: 6px; margin: 2px; }

/* ── slider override ── */
[data-testid="stSlider"] [data-baseweb="slider"] { margin-top: 4px; }

/* ── buttons ── */
.stButton > button {
  background: #1a212a !important;
  color: #eef2f5 !important;
  border: 1px solid rgba(255,255,255,.14) !important;
  border-radius: 9px !important;
  font-weight: 500 !important;
  font-family: 'IBM Plex Sans', sans-serif !important;
  transition: border-color .15s, color .15s !important;
}
.stButton > button:hover {
  border-color: #33c46a !important;
  color: #33c46a !important;
}

/* ── dataframe ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── footer ── */
.app-footer {
  text-align: center; color: #5e6b77; font-size: 11.5px;
  border-top: 1px solid rgba(255,255,255,.08);
  padding-top: 20px; margin-top: 56px;
}

/* ── info-box legacy compat ── */
.info-box {
  background: #141a1f; border-radius: 12px; padding: 14px 18px;
  border-left: 3px solid #4f9cf5; font-size: 13.5px;
  color: #8b98a4; margin-bottom: 16px; line-height: 1.6;
}
.info-box b, .info-box strong { color: #eef2f5; }
</style>
""", unsafe_allow_html=True)
