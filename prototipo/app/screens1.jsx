const { useState, useMemo } = React;

function Hero({ compact }) {
  return (
    <header className={`hero ${compact ? "hero-compact" : ""}`}>
      <div className="hero-lines" />
      <div className="hero-body">
        <div className="hero-tag"><Icon name="target" size={15} /> Análise preditiva · Machine Learning</div>
        <h1>Previsão de Rebaixamento<span className="hero-em"> — Brasileirão Série A 2025</span></h1>
        <p>Regressão Logística · Leonardo Feitosa — Ciência de Dados · UFPB</p>
      </div>
    </header>
  );
}

function Callout({ icon = "info", tone = "info", children, title }) {
  return (
    <div className={`callout callout-${tone}`}>
      <Icon name={icon} size={18} className="callout-ic" />
      <div>{title && <strong>{title} </strong>}{children}</div>
    </div>
  );
}

function SliderField({ label, icon, value, min, max, step = 1, onChange, fmt = (v) => v, hint, unit }) {
  return (
    <div className="field">
      <div className="field-head">
        <label>{icon && <Icon name={icon} size={15} />} {label}</label>
        <span className="field-val">{fmt(value)}{unit}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ "--pct": `${((value - min) / (max - min)) * 100}%` }} />
      <div className="field-scale"><span>{fmt(min)}</span><span>{fmt(max)}</span></div>
      {hint && <div className="field-hint">{hint}</div>}
    </div>
  );
}

/* ========================= PREVISÃO 2025 ========================= */
function ScreenPrevisao() {
  const M = window.MODEL;
  const [nome, setNome] = useState("Meu Clube");
  // elenco
  const [plantel, setPlantel] = useState(28);
  const [estr, setEstr]       = useState(4);
  const [vm, setVm]           = useState(85);
  // desempenho (médias históricas da liga como default)
  const [pts, setPts]         = useState(50);
  const [gPro, setGPro]       = useState(38);
  const [gContra, setGContra] = useState(35);
  const [vit, setVit]         = useState(14);

  // derivados automaticamente (consistentes com o real)
  const sg  = gPro - gContra;           // saldo de gols
  const apr = pts / 114;                // aproveitamento (0-1): 38 jogos × 3 pts = 114

  const p    = window.predictSimple(plantel, estr, vm, pts, sg, gPro, gContra, vit, apr * 100);
  const band = window.riskBand(p);

  const aprPct = Math.round(apr * 100);
  const med = { vm: 85, plantel: 28, estr: 4, pts: 50, sg: 3, gPro: 38, gContra: 35, vit: 14, apr: 44 };
  const fatores = [
    { l: "Valor de mercado",      v: vm,      ref: med.vm,      good: vm >= med.vm,          icon: "wallet",  txt: vm >= med.vm ? "acima da média" : "abaixo da média" },
    { l: "Pontos médios",         v: pts,     ref: med.pts,     good: pts >= med.pts,         icon: "activity",txt: pts >= med.pts ? "desempenho acima da média" : "desempenho abaixo da média" },
    { l: "Aproveitamento (auto)", v: aprPct,  ref: med.apr,     good: aprPct >= med.apr,      icon: "bars",    txt: `${aprPct}% — ${aprPct >= med.apr ? "bom" : "abaixo da média"}` },
    { l: "Saldo de gols (auto)",  v: sg,      ref: med.sg,      good: sg >= med.sg,           icon: "target",  txt: sg >= 0 ? `+${sg} (positivo)` : `${sg} (negativo)` },
    { l: "Gols marcados médios",  v: gPro,    ref: med.gPro,    good: gPro >= med.gPro,       icon: "up",      txt: gPro >= med.gPro ? "ataque eficiente" : "ataque abaixo da média" },
    { l: "Gols sofridos médios",  v: gContra, ref: med.gContra, good: gContra <= med.gContra, icon: "down",    txt: gContra <= med.gContra ? "defesa sólida" : "defesa vulnerável" },
    { l: "Vitórias médias",       v: vit,     ref: med.vit,     good: vit >= med.vit,         icon: "trophy",  txt: vit >= med.vit ? "acima da média" : "abaixo da média" },
  ];

  return (
    <div className="screen">
      <Hero />
      <Callout title="Modelo." tone="info" icon="target">
        <strong>Regressão Logística</strong> treinada com dados do Transfermarkt (2014–2022) e validada
        em 2023–2024 — <b>acurácia {window.fmtPct(M.acuracia, 0)}</b> · <b>AUC-ROC {window.fmtNum(M.aucTeste, 3)}</b>.
        Usa <b>15 features</b>: elenco + janelas deslizantes de desempenho (médias das últimas 3 e 5 temporadas).
      </Callout>

      <SectionTitle kicker="Ferramenta">Simulador individual de risco</SectionTitle>

      <div className="sim-grid">
        {/* coluna esquerda — inputs */}
        <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
          <Card>
            <div className="card-title"><Icon name="users" size={16} /> Identificação</div>
            <div className="field">
              <div className="field-head"><label>Nome do clube</label></div>
              <input className="text-input" value={nome} onChange={(e) => setNome(e.target.value)} />
            </div>
          </Card>

          <Card>
            <div className="card-title"><Icon name="wallet" size={16} /> Dados do elenco</div>
            <SliderField label="Tamanho do elenco" icon="users" value={plantel}
              min={15} max={55} onChange={setPlantel} unit=" atletas"
              hint="Média histórica na Série A: ~28 atletas." />
            <SliderField label="Nº de estrangeiros" icon="globe" value={estr}
              min={0} max={15} onChange={setEstr}
              hint="Atletas não-brasileiros. Média histórica: ~4." />
            <SliderField label="Valor de mercado total" icon="wallet" value={vm}
              min={5} max={300} step={1} onChange={setVm} unit=" M€"
              fmt={(v) => window.fmtNum(v, 0)}
              hint="Soma do valor de mercado do elenco (Transfermarkt). Média: ~85 M€." />
          </Card>

          <Card>
            <div className="card-title"><Icon name="activity" size={16} /> Desempenho histórico médio</div>
            <div style={{ fontSize:11.5, color:"var(--faint)", marginBottom:14, lineHeight:1.5 }}>
              Médias das últimas temporadas na Série A.
              <b> Saldo de gols</b> e <b>aproveitamento</b> são calculados automaticamente para manter consistência com os outros valores.
            </div>

            <SliderField label="Pontos médios" icon="target" value={pts}
              min={20} max={85} onChange={setPts} unit=" pts"
              hint="Pontos por temporada (38 jogos). Média na Série A: ~50 pts." />

            {/* valores derivados (display apenas) */}
            <div style={{ display:"flex", gap:10, marginBottom:18 }}>
              <div style={{ flex:1, background:"var(--surface-2)", border:"1px solid var(--border)", borderRadius:10, padding:"10px 14px" }}>
                <div style={{ fontSize:11, color:"var(--faint)", marginBottom:4 }}>Aproveitamento (auto)</div>
                <div style={{ fontFamily:"var(--mono)", fontSize:15, fontWeight:600, color:"var(--green)" }}>{aprPct}%</div>
                <div style={{ fontSize:10.5, color:"var(--faint)", marginTop:3 }}>pts ÷ 114 × 100</div>
              </div>
              <div style={{ flex:1, background:"var(--surface-2)", border:"1px solid var(--border)", borderRadius:10, padding:"10px 14px" }}>
                <div style={{ fontSize:11, color:"var(--faint)", marginBottom:4 }}>Saldo de gols (auto)</div>
                <div style={{ fontFamily:"var(--mono)", fontSize:15, fontWeight:600, color: sg >= 0 ? "var(--green)" : "var(--red)" }}>{sg >= 0 ? "+" : ""}{sg}</div>
                <div style={{ fontSize:10.5, color:"var(--faint)", marginTop:3 }}>marcados − sofridos</div>
              </div>
            </div>

            <SliderField label="Gols marcados (média)" icon="up" value={gPro}
              min={15} max={65} onChange={setGPro} unit=" gols"
              hint="Gols marcados por temporada. Média: ~38." />
            <SliderField label="Gols sofridos (média)" icon="down" value={gContra}
              min={15} max={65} onChange={setGContra} unit=" gols"
              hint="Gols sofridos por temporada. Média: ~35." />
            <SliderField label="Vitórias médias" icon="trophy" value={vit}
              min={0} max={30} onChange={setVit} unit=" vit."
              hint="Vitórias por temporada. Média: ~14." />
          </Card>
        </div>

        {/* coluna direita — resultado */}
        <Card className="result-card" style={{ position:"sticky", top:16, alignSelf:"start" }}>
          <div className="card-title"><Icon name="activity" size={16} /> Resultado da análise</div>
          <div className="result-gauge">
            <Gauge p={p} size={172} />
            <div className="result-club">
              <Crest club={{ nome, cor: band.cor }} size={22} />
              <span>{nome || "Clube"}</span>
            </div>
          </div>
          <div className="result-verdict" style={{ borderColor: band.cor }}>
            <Badge tone={band.key === "alto" ? "danger" : band.key === "medio" ? "warn" : "ok"}>
              {band.label}
            </Badge>
            <span>Probabilidade de rebaixamento estimada em <b>{window.fmtPct(p)}</b></span>
          </div>
          <div className="result-factors" style={{ marginTop:16 }}>
            <div style={{ fontSize:11, color:"var(--faint)", marginBottom:8, letterSpacing:".08em", textTransform:"uppercase", fontWeight:600 }}>
              Comparação com a média da liga
            </div>
            {fatores.map((f, i) => (
              <div className="rf" key={i}>
                <Icon name={f.icon} size={14} style={{ color: f.good ? "var(--green)" : "var(--red)", flexShrink:0 }} />
                <span className="rf-l" style={{ fontSize:12.5 }}>{f.l}</span>
                <span className="rf-tag" style={{ color: f.good ? "var(--green)" : "var(--red)", fontSize:11.5 }}>
                  {f.good ? "▲" : "▼"} {f.txt}
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Callout tone="muted" icon="info">
        Todos os 15 parâmetros do modelo são usados. Gols sofridos e elencos numerosos sem qualidade
        tendem a <b>aumentar</b> o risco; valor de mercado alto, pontos e aproveitamento elevados o <b>reduzem</b>.
        Veja <b>Análise de Sensibilidade</b> para o efeito isolado de cada variável.
      </Callout>
    </div>
  );
}

/* ========================= RANKING 2025 ========================= */
function ScreenRanking() {
  const rank = useMemo(() => window.ranking2025(), []);
  const [sel, setSel] = useState(null);
  const zonaCorte = 4;
  const media = rank.reduce((a, c) => a + c.prob, 0) / rank.length;

  return (
    <div className="screen">
      <Hero compact />
      <SectionTitle kicker="Projeção do modelo">Ranking de risco — 20 clubes da Série A 2025</SectionTitle>
      <Callout tone="warn" icon="flame">
        <strong>Leitura:</strong> probabilidade individual de rebaixamento estimada pelo modelo a partir
        do elenco e do desempenho recente de cada clube. Os <b>4 mais prováveis</b> formam a zona de
        rebaixamento projetada (destaque em vermelho).
      </Callout>

      <div className="rank-kpis">
        <StatCard label="Clubes analisados" value={rank.length} />
        <StatCard label="Risco médio da liga" value={window.fmtPct(media, 1)} accent="var(--amber)" />
        <StatCard label="Zona de rebaixamento" value={zonaCorte} unit=" clubes" accent="var(--red)" />
        <StatCard label="Mais seguro" value={rank[rank.length - 1].nome}
          sub={window.fmtPct(rank[rank.length - 1].prob)} accent="var(--green)" />
      </div>

      <Card pad={false} className="rank-card">
        <div className="rank-head">
          <span className="rk-pos">#</span>
          <span className="rk-club">Clube</span>
          <span className="rk-bar">Probabilidade de rebaixamento</span>
          <span className="rk-pct">Risco</span>
          <span className="rk-vm">VM (M€)</span>
        </div>
        {rank.map((c, i) => {
          const zona = i < zonaCorte;
          const band = window.riskBand(c.prob);
          return (
            <div key={c.nome}
              className={`rank-row ${zona ? "rank-zone" : ""} ${sel === c.nome ? "rank-sel" : ""}`}
              onClick={() => setSel(sel === c.nome ? null : c.nome)}>
              <span className="rk-pos">
                <span className="rk-num" style={zona ? { color: "var(--red)" } : null}>{i + 1}</span>
              </span>
              <span className="rk-club">
                <Crest club={c} size={26} />
                <span className="rk-name">{c.nome}</span>
                {c.promovido && <Badge tone="neutral" style={{ marginLeft: 6, fontSize: 10 }}>Promovido</Badge>}
                <span className="rk-uf">{c.uf}</span>
              </span>
              <span className="rk-bar"><ProbBar p={c.prob} height={10} /></span>
              <span className="rk-pct" style={{ color: band.cor }}>{window.fmtPct(c.prob, 1)}</span>
              <span className="rk-vm">{window.fmtNum(c.vm, 0)}</span>
            </div>
          );
        })}
        <div className="rank-corte">
          <Icon name="scale" size={13} /> linha de corte — 4º / 5º colocado projetado
        </div>
      </Card>

      <Callout tone="muted" icon="info">
        Projeção ilustrativa do modelo do TCC para fins acadêmicos; não constitui aposta ou
        previsão oficial. Probabilidades individuais — a soma não é normalizada para exatamente 4.
      </Callout>
    </div>
  );
}

/* ========================= DESEMPENHO DO MODELO ========================= */
function ScreenModelo() {
  const M = window.MODEL, cf = window.CONFUSION;
  const prec = cf.tp / (cf.tp + cf.fp);
  const rec  = cf.tp / (cf.tp + cf.fn);
  const f1   = 2 * prec * rec / (prec + rec);

  return (
    <div className="screen">
      <Hero compact />
      <SectionTitle kicker="Avaliação">Desempenho do modelo</SectionTitle>
      <Callout tone="info" icon="info">
        Em rebaixamento as classes são desbalanceadas (~20% positivos), então a <b>acurácia
        sozinha engana</b>. Por isso reportamos <b>precisão, recall, F1, ROC e calibração</b> —
        o <b>recall da classe "rebaixado"</b> é a métrica que mais importa.
      </Callout>

      <div className="metric-row">
        <StatCard label="Acurácia" value={window.fmtPct(M.acuracia, 0)} sub="teste 2023–24" />
        <StatCard label="Precisão" value={window.fmtNum(prec, 2)} sub="dos previstos, quantos caíram" accent="var(--blue)" />
        <StatCard label="Recall (rebaixado)" value={window.fmtNum(rec, 2)} sub="dos que caíram, quantos achamos" accent="var(--green)" />
        <StatCard label="F1-score" value={window.fmtNum(f1, 2)} sub="equilíbrio prec.×recall" accent="var(--amber)" />
        <StatCard label="AUC-ROC" value={window.fmtNum(M.aucTeste, 3)} sub="teste" />
        <StatCard label="AUC-ROC (CV)" value={`${window.fmtNum(M.aucCV, 3)}`}
          sub={`± ${window.fmtNum(M.aucCVstd, 3)} · walk-forward`} />
      </div>

      <div className="chart-trio">
        <Card>
          <div className="card-title"><Icon name="grid" size={16} /> Matriz de confusão</div>
          <Confusion m={cf} />
        </Card>
        <Card>
          <div className="card-title"><Icon name="activity" size={16} /> Curva ROC</div>
          <RocCurve pts={window.ROC} auc={M.aucTeste} />
        </Card>
        <Card>
          <div className="card-title"><Icon name="scale" size={16} /> Calibração</div>
          <CalibCurve pts={window.CALIB} />
          <div className="mini-note">Pontos próximos da diagonal = probabilidades confiáveis.</div>
        </Card>
      </div>

      <SectionTitle kicker="Comparação">Por que Regressão Logística?</SectionTitle>
      <Card pad={false}>
        <div className="comp-table">
          <div className="comp-head">
            <span>Algoritmo</span><span>AUC-ROC (CV)</span><span>AUC-ROC (teste)</span><span>Acurácia</span><span>F1</span><span>Observação</span>
          </div>
          {window.MODELOS_COMP.map((m) => (
            <div key={m.sigla} className={`comp-row ${m.escolhido ? "comp-on" : ""}`}>
              <span className="comp-name">
                {m.escolhido && <Icon name="check" size={15} className="comp-check" />}
                {m.nome} <em>{m.sigla}</em>
              </span>
              <span className="mono">{window.fmtNum(m.auc, 3)}</span>
              <span className="mono">{window.fmtNum(m.aucTeste, 3)}</span>
              <span className="mono">{window.fmtPct(m.acc, 0)}</span>
              <span className="mono">{window.fmtNum(m.f1, 2)}</span>
              <span className="comp-note">{m.nota}</span>
            </div>
          ))}
        </div>
      </Card>

      <SectionTitle kicker="Interpretabilidade">Coeficientes — odds ratios</SectionTitle>
      <Callout tone="muted" icon="info">
        Odds ratio &lt; 1 = a variável <b>reduz</b> a chance de rebaixamento; &gt; 1 = <b>aumenta</b>.
        Barras à esquerda do 1,0 protegem; à direita, agravam.
      </Callout>
      <Card>
        <div className="or-chart">
          {window.COEFS.map((c) => {
            const protege = c.or < 1;
            const logOR = Math.log(c.or);
            const span = 2.0;
            const left = 50 + (logOR / span) * 50;
            return (
              <div className="or-row" key={c.feat}>
                <span className="or-feat">{c.feat}</span>
                <div className="or-track">
                  <div className="or-axis" />
                  <div className="or-bar" style={{
                    left: protege ? `${left}%` : "50%",
                    width: `${Math.abs(left - 50)}%`,
                    background: protege ? "var(--green)" : "var(--red)",
                  }} />
                </div>
                <span className="or-val mono" style={{ color: protege ? "var(--green)" : "var(--red)" }}>
                  {window.fmtNum(c.or, 2)}
                </span>
              </div>
            );
          })}
          <div className="or-axislabels"><span>protege ←</span><span>1,0</span><span>→ agrava</span></div>
        </div>
      </Card>
    </div>
  );
}

Object.assign(window, { Hero, Callout, SliderField, ScreenPrevisao, ScreenRanking, ScreenModelo });
