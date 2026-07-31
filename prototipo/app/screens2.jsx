/* ========================= DADOS HISTÓRICOS ========================= */
function ScreenHistorico() {
  const [sit, setSit] = useState(["Rebaixado", "Série A", "Top 4"]);
  const [tab, setTab] = useState("comp");
  const M = window.MODEL;

  const toggleSit = (s) =>
    setSit((cur) => cur.includes(s) ? cur.filter((x) => x !== s) : [...cur, s]);

  const vmData = (window.VM_MEDIO || []).map(([l, v]) => ({ label: l, value: v }));

  return (
    <div className="screen">
      <Hero compact />
      <SectionTitle kicker="Base de dados">Histórico — Brasileirão Série A</SectionTitle>

      <Card className="filters">
        <div className="card-title"><Icon name="filter" size={16} /> Filtros</div>
        <div className="filter-grid">
          <div className="filter-col">
            <label>Situação</label>
            <div className="chips">
              {["Rebaixado", "Série A", "Top 4"].map((s) => (
                <button key={s} className={`chip ${sit.includes(s) ? "chip-on" : ""}`} onClick={() => toggleSit(s)}>
                  {s} {sit.includes(s) && <Icon name="x" size={12} />}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      <div className="hist-kpis">
        <StatCard label="Registros" value={M.registros} />
        <StatCard label="Clubes únicos" value={M.clubesUnicos} />
        <StatCard label="Temporadas" value={M.temporadas} />
        <StatCard label="Rebaixamentos" value={M.rebaixamentos} accent="var(--red)" />
      </div>

      <Card pad={false}>
        <div className="data-table">
          <div className="dt-head dt-grid">
            <span>#</span><span>Clube</span><span>Temporada</span>
            <span>Plantel</span><span>Estr.</span><span>VM (M€)</span><span>Situação</span>
          </div>
          {(window.HIST_SAMPLE || []).map((r, idx) => (
            <div className="dt-row dt-grid" key={idx}>
              <span className="dt-mut">{idx}</span>
              <span>{r.clube}</span>
              <span className="mono">{r.temp}</span>
              <span className="mono">{r.plantel}</span>
              <span className="mono">{r.estr}</span>
              <span className="mono">{window.fmtNum(r.vm, 2)}</span>
              <span><Badge tone={r.sit === "Top 4" ? "ok" : r.sit === "Rebaixado" ? "danger" : "neutral"}>{r.sit}</Badge></span>
            </div>
          ))}
        </div>
        <div className="dt-footer">
          <span className="dt-mut">Exibindo amostra de {(window.HIST_SAMPLE || []).length} de {M.registros} registros</span>
        </div>
      </Card>

      <Tabs active={tab} onChange={setTab} tabs={[
        { id: "comp", label: "Comparação entre clubes", icon: "bars" },
        { id: "dist", label: "Distribuição por situação", icon: "target" },
        { id: "evo",  label: "Evolução temporal", icon: "activity" },
        { id: "jan",  label: "Janelas deslizantes", icon: "layers" },
      ]} />

      {tab === "comp" && (
        <Card>
          <div className="card-title">Top 20 clubes — VM Total médio (M€)</div>
          <VBars data={vmData} color="var(--green)" highlight={0} fmt={(v) => window.fmtNum(v, 1)} />
        </Card>
      )}
      {tab === "dist" && (
        <Card>
          <div className="card-title">Distribuição por situação</div>
          <div className="dist-grid">
            {[["Top 4", 44, "var(--green)"], ["Série A", 132, "var(--blue)"], ["Rebaixado", 44, "var(--red)"]].map(([l, v, c]) => (
              <div className="dist-cell" key={l}>
                <div className="dist-big" style={{ color: c }}>{v}</div>
                <div className="dist-lbl">{l}</div>
                <div className="dist-bar"><div style={{ width: `${(v / 220) * 100}%`, background: c }} /></div>
                <div className="dt-mut">{window.fmtPct(v / 220, 0)} dos registros</div>
              </div>
            ))}
          </div>
        </Card>
      )}
      {tab === "evo" && (
        <Card>
          <div className="card-title">Rebaixamentos por temporada (2014–2024)</div>
          <VBars height={260} color="var(--red)" highlight={-1}
            data={[2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024].map((t) => ({ label: t, value: 4 }))}
            fmt={(v) => v} />
          <div className="mini-note">4 clubes rebaixados por temporada — regra estável da Série A no período.</div>
        </Card>
      )}
      {tab === "jan" && (
        <Card>
          <div className="card-title">Janelas deslizantes de desempenho</div>
          <div className="jan-grid">
            {(window.FEATURES.janelas || []).map((j, i) => (
              <div className="jan-cell" key={i}><Icon name="layers" size={15} /> {j}</div>
            ))}
          </div>
          <div className="mini-note">Médias móveis das últimas 3 e 5 temporadas capturam tendência recente — 12 das 15 features.</div>
        </Card>
      )}
    </div>
  );
}

/* ========================= SENSIBILIDADE ========================= */
function ScreenSensibilidade() {
  const B = window.SENS_BASE;
  // As faixas vêm dos mínimos e máximos observados na base — antes eram fixas
  // em [15, 50] para o plantel, faixa que nem existe nos dados (real: 41–80).
  const F = window.SENS_FAIXAS || { plantel: [41, 82], estr: [0, 17], vm: [5, 285] };
  const curves = [
    { name: "plantel", range: F.plantel, xLabel: "Tamanho do elenco", color: "var(--blue)", base: B.plantel, fill: false, title: "Impacto do tamanho do elenco" },
    { name: "estr",    range: F.estr,  xLabel: "Nº de estrangeiros", color: "var(--violet)", base: B.estr, fill: false, title: "Impacto do nº de estrangeiros" },
    { name: "vm",      range: F.vm, xLabel: "Valor de mercado (M€)", color: "var(--red)", base: B.vm,  fill: true,  title: "Impacto do valor de mercado" },
  ];

  return (
    <div className="screen">
      <Hero compact />
      <SectionTitle kicker="Interpretação">Análise de sensibilidade</SectionTitle>
      <Callout tone="info" icon="info">
        Mostra como cada variável influencia a probabilidade de rebaixamento, mantendo as demais
        fixas nos <b>valores médios históricos</b> (Plantel {B.plantel} · Estrangeiros {B.estr} · VM {B.vm} M€).
      </Callout>

      <div className="sens-kpis">
        <StatCard label="Plantel base" value={B.plantel} unit=" atletas" />
        <StatCard label="Estrangeiros base" value={B.estr} />
        <StatCard label="Valor de mercado base" value={B.vm} unit=" M€" />
      </div>

      <div className="sens-grid">
        {curves.map((c) => (
          <Card key={c.name}>
            <div className="card-title">{c.title}</div>
            <LineChart pts={window.sensCurve(c.name, c.range)} xRange={c.range}
              xLabel={c.xLabel} color={c.color} baseX={c.base} fill={c.fill} />
          </Card>
        ))}
      </div>

      <Callout tone="muted" icon="info">
        <strong>Interpretação:</strong> curvas <i>descendentes</i> indicam que aumentar a variável
        <b> reduz</b> o risco. O <b>valor de mercado</b> é o fator mais decisivo (queda acentuada);
        o nº de estrangeiros tem efeito quase neutro. A linha tracejada vermelha marca o limiar de 50%.
      </Callout>
    </div>
  );
}

/* ========================= DESCRITIVA ========================= */
function ScreenDescritiva() {
  // O seletor de temporada era um <div> decorativo com "2024" fixo — agora é um
  // <select> real ligado a DESC_BY_SEASON, que traz todas as temporadas rotuladas.
  const porTemporada = window.DESC_BY_SEASON || { "2024": window.DESC_2024 };
  const temporadas = window.DESC_TEMPORADAS ||
    Object.keys(porTemporada).sort();
  const [ano, setAno] = useState(temporadas[temporadas.length - 1]);
  const D = porTemporada[ano] || window.DESC_2024;
  const [tab, setTab] = useState("stats");
  const boxColors = ["var(--blue)", "var(--red)", "var(--green)", "var(--violet)"];

  return (
    <div className="screen">
      <Hero compact />
      <SectionTitle kicker="Estatística">Análise descritiva</SectionTitle>

      <div className="desc-season">
        <label htmlFor="sel-temporada">Temporada para análise</label>
        <select
          id="sel-temporada"
          className="select select-sm"
          value={ano}
          onChange={(e) => setAno(e.target.value)}
        >
          {temporadas.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      <div className="desc-kpis">
        <StatCard label="Clubes" value={D.resumo.clubes} />
        <StatCard label="Plantel médio" value={window.fmtNum(D.resumo.plantelMedio, 1)} unit=" atletas" />
        <StatCard label="VM médio" value={window.fmtNum(D.resumo.vmMedio, 1)} unit=" M€" accent="var(--green)" />
        <StatCard label="Pontos médios" value={window.fmtNum(D.resumo.ptsMedio, 1)} accent="var(--blue)" />
      </div>

      <Tabs active={tab} onChange={setTab} tabs={[
        { id: "stats", label: "Estatísticas descritivas", icon: "bars" },
        { id: "clube", label: "Análise por clube", icon: "search" },
        { id: "dist",  label: "Distribuição", icon: "activity" },
      ]} />

      {tab === "stats" && (
        <Card pad={false}>
          <div className="stats-table">
            <div className="st-head st-grid">
              <span>Variável</span><span>N</span><span>Média</span><span>Desv.Pad.</span>
              <span>Mín</span><span>Q1</span><span>Mediana</span><span>Q3</span><span>Máx</span>
            </div>
            {D.stats.map((s) => (
              <div className="st-row st-grid" key={s.v}>
                <span className="st-name">{s.v}</span>
                <span className="mono">{s.n}</span>
                <span className="mono">{window.fmtNum(s.media, 2)}</span>
                <span className="mono">{window.fmtNum(s.std, 2)}</span>
                <span className="mono">{window.fmtNum(s.min, 1)}</span>
                <span className="mono">{window.fmtNum(s.q1, 2)}</span>
                <span className="mono">{window.fmtNum(s.med, 1)}</span>
                <span className="mono">{window.fmtNum(s.q3, 2)}</span>
                <span className="mono">{window.fmtNum(s.max, 1)}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {tab === "clube" && (
        <Card pad={false}>
          <div className="data-table">
            <div className="dt-head clube-grid">
              <span>Clube</span><span>Plantel</span><span>Estr.</span><span>VM (M€)</span><span>Pontos</span>
            </div>
            {D.clubes.map((c) => (
              <div className="dt-row clube-grid" key={c.clube}>
                <span className="dt-club">
                  <Crest club={window.CLUBES_2025.find(x => x.nome === c.clube) || { nome: c.clube, cor: "#555" }} size={22} />
                  {" "}{c.clube}
                </span>
                <span className="mono">{c.plantel}</span>
                <span className="mono">{c.estr}</span>
                <span className="mono">{window.fmtNum(c.vm, 2)}</span>
                <span className="mono st-pts">{c.pts}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {tab === "dist" && (
        <Card>
          <div className="card-title">Distribuição das variáveis — 2024</div>
          <div className="boxplots">
            {D.stats.map((s, i) => (
              <BoxRow key={s.v} stat={s} color={boxColors[i]}
                scaleMax={s.v === "VM Total (M€)" ? 220 : s.max * 1.1} />
            ))}
          </div>
          <div className="mini-note">Caixa = intervalo interquartil (Q1–Q3) · linha central = mediana · hastes = mín/máx.</div>
        </Card>
      )}
    </div>
  );
}

Object.assign(window, { ScreenHistorico, ScreenSensibilidade, ScreenDescritiva });
