const ICONS = {
  trophy: "M6 9a6 6 0 0 0 12 0V4H6v5ZM6 4H3v2a3 3 0 0 0 3 3M18 4h3v2a3 3 0 0 1-3 3M9 18h6M12 14v4M8 21h8",
  history: "M3 12a9 9 0 1 0 3-6.7L3 8M3 4v4h4M12 8v4l3 2",
  sliders: "M4 6h10M18 6h2M4 12h2M10 12h10M4 18h8M16 18h4M14 4v4M6 10v4M12 16v4",
  bars: "M4 20V10M10 20V4M16 20v-8M22 20H2",
  target: "M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0-18 0M12 12m-5 0a5 5 0 1 0 10 0a5 5 0 1 0-10 0M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0-2 0",
  users: "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM22 21v-2a4 4 0 0 0-3-3.87M16 3.13A4 4 0 0 1 16 11",
  globe: "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20ZM2 12h20M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20Z",
  wallet: "M20 7H5a2 2 0 0 1 0-4h13v4M3 5v14a2 2 0 0 0 2 2h16V7M16 14h.01",
  download: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3",
  chevron: "M6 9l6 6 6-6",
  check: "M20 6L9 17l-5-5",
  x: "M18 6L6 18M6 6l12 12",
  search: "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16ZM21 21l-4.3-4.3",
  flame: "M12 2c1 3 4 5 4 9a4 4 0 0 1-8 0c0-1 .3-2 1-3 .3 2 1.5 2.5 1.5 2.5C10 9 9 7 12 2Z",
  shield: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z",
  down: "M22 17l-8.5-8.5-5 5L2 7M16 17h6v-6",
  up: "M22 7l-8.5 8.5-5-5L2 17M16 7h6v6",
  info: "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20ZM12 16v-4M12 8h.01",
  grid: "M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z",
  activity: "M22 12h-4l-3 9L9 3l-3 9H2",
  scale: "M12 3v18M5 7l-3 6a4 4 0 0 0 6 0L5 7ZM19 7l-3 6a4 4 0 0 0 6 0l-3-6ZM7 21h10M5 7l7-2 7 2",
  layers: "M12 2 2 7l10 5 10-5-10-5ZM2 17l10 5 10-5M2 12l10 5 10-5",
  filter: "M22 3H2l8 9.46V19l4 2v-8.54L22 3Z",
};

function Icon({ name, size = 18, stroke = 2, style, className }) {
  const d = ICONS[name];
  if (!d) return null;
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth={stroke}
      strokeLinecap="round" strokeLinejoin="round" style={style}>
      {d.split("M").filter(Boolean).map((seg, i) => <path key={i} d={"M" + seg} />)}
    </svg>
  );
}

function SectionTitle({ kicker, children, right }) {
  return (
    <div className="sec-title">
      <div>
        {kicker && <div className="sec-kicker">{kicker}</div>}
        <h2>{children}</h2>
      </div>
      {right}
    </div>
  );
}

function Card({ children, className = "", style, pad = true }) {
  return <div className={`card ${pad ? "card-pad" : ""} ${className}`} style={style}>{children}</div>;
}

function StatCard({ label, value, unit, sub, accent }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={accent ? { color: accent } : null}>
        {value}{unit && <span className="stat-unit">{unit}</span>}
      </div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

function Tabs({ tabs, active, onChange }) {
  return (
    <div className="tabs">
      {tabs.map((t) => (
        <button key={t.id}
          className={`tab ${active === t.id ? "tab-on" : ""}`}
          onClick={() => onChange(t.id)}>
          {t.icon && <Icon name={t.icon} size={16} />}
          <span>{t.label}</span>
        </button>
      ))}
    </div>
  );
}

function Badge({ children, tone = "neutral", style }) {
  return <span className={`badge badge-${tone}`} style={style}>{children}</span>;
}

function Crest({ club, size = 28 }) {
  const words = (club.nome || "").split(" ").filter((w) => w.length > 2);
  const initials = (words.length >= 2
    ? words.slice(0, 2).map((w) => w[0]).join("")
    : (club.nome || "??").replace(/[^A-Za-zÀ-ÿ]/g, "").slice(0, 2)).toUpperCase();
  return (
    <span className="crest" style={{
      width: size, height: size, background: club.cor || "#3a3a3a",
      fontSize: size * 0.38,
    }}>{initials}</span>
  );
}

function ProbBar({ p, height = 8, showZone = true }) {
  const band = window.riskBand(p);
  return (
    <div className="probbar" style={{ height }}>
      {showZone && <div className="probbar-zone" />}
      <div className="probbar-fill" style={{ width: `${Math.min(100, p * 100)}%`, background: band.cor }} />
    </div>
  );
}

Object.assign(window, { Icon, ICONS, SectionTitle, Card, StatCard, Tabs, Badge, Crest, ProbBar });
