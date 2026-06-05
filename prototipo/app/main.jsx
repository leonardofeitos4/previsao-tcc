const NAV = [
  { id: "previsao",  label: "Previsão 2025",        icon: "target",  screen: "ScreenPrevisao" },
  { id: "ranking",   label: "Ranking 2025",          icon: "trophy",  screen: "ScreenRanking" },
  { id: "modelo",    label: "Desempenho do Modelo",  icon: "activity",screen: "ScreenModelo" },
  { id: "historico", label: "Dados Históricos",      icon: "history", screen: "ScreenHistorico" },
  { id: "sensib",    label: "Análise de Sensibilidade", icon: "sliders", screen: "ScreenSensibilidade" },
  { id: "descritiva",label: "Análise Descritiva",    icon: "bars",    screen: "ScreenDescritiva" },
];

function ModelMini() {
  const M = window.MODEL;
  const rows = [
    ["Algoritmo", "Reg. Logística"],
    ["Treino", M.treino],
    ["Teste", M.teste],
    ["Acurácia (teste)", window.fmtPct(M.acuracia, 0)],
    ["AUC-ROC (teste)", window.fmtNum(M.aucTeste, 3)],
    ["AUC-ROC (CV)", `${window.fmtNum(M.aucCV, 3)} ± ${window.fmtNum(M.aucCVstd, 3)}`],
    ["Validação", M.validacao],
    ["Modelos testados", M.modelosTestados.join(" · ")],
  ];
  return (
    <div className="model-mini">
      <div className="mm-title">Sobre o modelo</div>
      {rows.map(([k, v]) => (
        <div className="mm-row" key={k}><span>{k}</span><b>{v}</b></div>
      ))}
      <div className="mm-feat">
        <div className="mm-feat-h"><Icon name="layers" size={13} /> 15 features</div>
        <div className="mm-feat-tags">
          <span><Icon name="users" size={12} /> Plantel</span>
          <span><Icon name="globe" size={12} /> Estrangeiros</span>
          <span><Icon name="wallet" size={12} /> Valor de mercado</span>
          <span><Icon name="layers" size={12} /> 12 janelas</span>
        </div>
      </div>
    </div>
  );
}

function Sidebar({ active, onNav, open, setOpen }) {
  return (
    <>
      <aside className={`sidebar ${open ? "" : "sb-closed"}`}>
        <div className="sb-brand">
          <span className="sb-logo"><Icon name="shield" size={20} /></span>
          <div>
            <div className="sb-title">Série A 2025</div>
            <div className="sb-sub">Previsão de Rebaixamento</div>
          </div>
          <button className="sb-close" onClick={() => setOpen(false)}><Icon name="x" size={18} /></button>
        </div>

        <nav className="sb-nav">
          <div className="sb-navlabel">Navegação</div>
          {NAV.map((n) => (
            <button key={n.id} className={`nav-item ${active === n.id ? "nav-on" : ""}`} onClick={() => onNav(n.id)}>
              <span className="nav-dot" />
              <Icon name={n.icon} size={17} />
              <span className="nav-label">{n.label}</span>
              {n.novo && <span className="nav-new">novo</span>}
            </button>
          ))}
        </nav>

        <ModelMini />
        <div className="sb-foot">TCC · Leonardo Feitosa · Ciência de Dados – UFPB · 2025</div>
      </aside>
      {!open && (
        <button className="sb-open" onClick={() => setOpen(true)}><Icon name="grid" size={18} /></button>
      )}
    </>
  );
}

function App() {
  const [active, setActive] = React.useState("previsao");
  const [open, setOpen] = React.useState(true);
  const nav = NAV.find((n) => n.id === active);
  const Screen = window[nav.screen];

  const go = (id) => { setActive(id); window.scrollTo({ top: 0 }); };

  return (
    <div className={`app ${open ? "" : "app-wide"}`}>
      <Sidebar active={active} onNav={go} open={open} setOpen={setOpen} />
      <main className="main">
        <Screen key={active} />
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
