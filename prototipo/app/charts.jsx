function Gauge({ p, size = 150 }) {
  const band = window.riskBand(p);
  const r = size / 2 - 14;
  const cx = size / 2, cy = size / 2;
  const start = Math.PI * 0.75, end = Math.PI * 2.25;
  const a = start + (end - start) * Math.min(1, p);
  const pol = (ang, rad) => [cx + rad * Math.cos(ang), cy + rad * Math.sin(ang)];
  const arc = (a0, a1, rad) => {
    const [x0, y0] = pol(a0, rad), [x1, y1] = pol(a1, rad);
    const large = a1 - a0 > Math.PI ? 1 : 0;
    return `M ${x0} ${y0} A ${rad} ${rad} 0 ${large} 1 ${x1} ${y1}`;
  };
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <path d={arc(start, end, r)} fill="none" stroke="var(--surface-3)" strokeWidth="12" strokeLinecap="round" />
      <path d={arc(start, a, r)} fill="none" stroke={band.cor} strokeWidth="12" strokeLinecap="round" />
      <text x={cx} y={cy - 2} textAnchor="middle" className="gauge-val" style={{ fill: band.cor }}>
        {window.fmtPct(p, 0)}
      </text>
      <text x={cx} y={cy + 20} textAnchor="middle" className="gauge-lbl">{band.label}</text>
    </svg>
  );
}

function VBars({ data, height = 320, fmt = (v) => v, color = "var(--green)", highlight = 0 }) {
  const W = 1000, H = height, padL = 44, padB = 86, padT = 16;
  const max = Math.max(...data.map((d) => d.value)) * 1.12;
  const bw = (W - padL - 10) / data.length;
  const y = (v) => padT + (H - padT - padB) * (1 - v / max);
  const ticks = 5;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="vbars" preserveAspectRatio="xMidYMid meet">
      {Array.from({ length: ticks + 1 }).map((_, i) => {
        const v = (max / ticks) * i;
        return (
          <g key={i}>
            <line x1={padL} x2={W - 6} y1={y(v)} y2={y(v)} stroke="var(--grid)" />
            <text x={padL - 8} y={y(v) + 4} textAnchor="end" className="ax">{Math.round(v)}</text>
          </g>
        );
      })}
      {data.map((d, i) => {
        const x = padL + i * bw + bw * 0.16;
        const w = bw * 0.68;
        const hh = (H - padT - padB) - (y(d.value) - padT);
        return (
          <g key={i}>
            <rect x={x} y={y(d.value)} width={w} height={Math.max(0, hh)} rx="3"
              fill={i === highlight ? color : "var(--bar-dim)"} />
            <text x={x + w / 2} y={y(d.value) - 6} textAnchor="middle" className="ax-val">{fmt(d.value)}</text>
            <text x={x + w / 2} y={H - padB + 16} textAnchor="end" className="ax-cat"
              transform={`rotate(-40 ${x + w / 2} ${H - padB + 16})`}>{d.label}</text>
          </g>
        );
      })}
    </svg>
  );
}

function LineChart({ pts, xRange, yRange = [0, 1], xLabel, color = "var(--blue)",
  threshold = 0.5, baseX, height = 230, fill = false }) {
  const W = 360, H = height, padL = 42, padB = 34, padT = 14, padR = 12;
  const [x0, x1] = xRange, [y0, y1] = yRange;
  const X = (x) => padL + (W - padL - padR) * ((x - x0) / (x1 - x0));
  const Y = (y) => padT + (H - padT - padB) * (1 - (y - y0) / (y1 - y0));
  const d = pts.map((p, i) => `${i ? "L" : "M"} ${X(p[0]).toFixed(1)} ${Y(p[1]).toFixed(1)}`).join(" ");
  const area = `${d} L ${X(pts[pts.length - 1][0])} ${Y(0)} L ${X(pts[0][0])} ${Y(0)} Z`;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="linechart" preserveAspectRatio="xMidYMid meet">
      {[0, 0.2, 0.4, 0.6, 0.8, 1].map((g) => (
        <g key={g}>
          <line x1={padL} x2={W - padR} y1={Y(g)} y2={Y(g)} stroke="var(--grid)" />
          <text x={padL - 6} y={Y(g) + 4} textAnchor="end" className="ax">{Math.round(g * 100)}%</text>
        </g>
      ))}
      <line x1={padL} x2={W - padR} y1={Y(threshold)} y2={Y(threshold)}
        stroke="var(--red)" strokeDasharray="5 4" strokeWidth="1.5" opacity="0.8" />
      {baseX != null && (
        <g>
          <line x1={X(baseX)} x2={X(baseX)} y1={padT} y2={H - padB} stroke="var(--muted)" strokeDasharray="3 3" />
          <text x={X(baseX) + 4} y={padT + 10} className="ax" style={{ fontSize: 10 }}>Base</text>
        </g>
      )}
      {fill && <path d={area} fill={color} opacity="0.12" />}
      <path d={d} fill="none" stroke={color} strokeWidth="2.5" />
      {[x0, (x0 + x1) / 2, x1].map((t, i) => (
        <text key={i} x={X(t)} y={H - padB + 16} textAnchor="middle" className="ax">{Math.round(t)}</text>
      ))}
      <text x={(W + padL) / 2} y={H - 4} textAnchor="middle" className="ax-title">{xLabel}</text>
    </svg>
  );
}

function RocCurve({ pts, auc, size = 300 }) {
  const W = size, H = size, pad = 38;
  const X = (x) => pad + (W - pad * 1.4) * x;
  const Y = (y) => H - pad - (H - pad * 1.4) * y;
  const d = pts.map((p, i) => `${i ? "L" : "M"} ${X(p[0]).toFixed(1)} ${Y(p[1]).toFixed(1)}`).join(" ");
  const area = `${d} L ${X(1)} ${Y(0)} Z`;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="roc" preserveAspectRatio="xMidYMid meet">
      {[0, .25, .5, .75, 1].map((g) => (
        <g key={g}>
          <line x1={X(g)} x2={X(g)} y1={Y(0)} y2={Y(1)} stroke="var(--grid)" />
          <line x1={X(0)} x2={X(1)} y1={Y(g)} y2={Y(g)} stroke="var(--grid)" />
        </g>
      ))}
      <line x1={X(0)} y1={Y(0)} x2={X(1)} y2={Y(1)} stroke="var(--muted)" strokeDasharray="5 4" />
      <path d={area} fill="var(--green)" opacity="0.12" />
      <path d={d} fill="none" stroke="var(--green)" strokeWidth="2.5" />
      <text x={X(0.55)} y={Y(0.25)} className="roc-auc">AUC {window.fmtNum(auc, 3)}</text>
      <text x={W / 2} y={H - 6} textAnchor="middle" className="ax-title">Taxa de Falso Positivo</text>
      <text x={12} y={H / 2} textAnchor="middle" className="ax-title"
        transform={`rotate(-90 12 ${H / 2})`}>Taxa de Verdadeiro Positivo</text>
    </svg>
  );
}

function CalibCurve({ pts, size = 300 }) {
  const W = size, H = size, pad = 38;
  const X = (x) => pad + (W - pad * 1.4) * x;
  const Y = (y) => H - pad - (H - pad * 1.4) * y;
  const d = pts.map((p, i) => `${i ? "L" : "M"} ${X(p[0]).toFixed(1)} ${Y(p[1]).toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="roc" preserveAspectRatio="xMidYMid meet">
      {[0, .25, .5, .75, 1].map((g) => (
        <line key={g} x1={X(g)} x2={X(g)} y1={Y(0)} y2={Y(1)} stroke="var(--grid)" />
      ))}
      <line x1={X(0)} y1={Y(0)} x2={X(1)} y2={Y(1)} stroke="var(--muted)" strokeDasharray="5 4" />
      <path d={d} fill="none" stroke="var(--blue)" strokeWidth="2.5" />
      {pts.map((p, i) => <circle key={i} cx={X(p[0])} cy={Y(p[1])} r="3.2" fill="var(--blue)" />)}
      <text x={W / 2} y={H - 6} textAnchor="middle" className="ax-title">Probabilidade prevista</text>
      <text x={12} y={H / 2} textAnchor="middle" className="ax-title"
        transform={`rotate(-90 12 ${H / 2})`}>Fração observada</text>
    </svg>
  );
}

function Confusion({ m }) {
  const cells = [
    { v: m.tn, l: "Verd. Negativo", good: true },
    { v: m.fp, l: "Falso Positivo", good: false },
    { v: m.fn, l: "Falso Negativo", good: false },
    { v: m.tp, l: "Verd. Positivo", good: true },
  ];
  const total = m.tn + m.fp + m.fn + m.tp;
  return (
    <div className="confusion">
      <div className="cf-corner" />
      <div className="cf-coltop">Previsto: Permanece</div>
      <div className="cf-coltop">Previsto: Rebaixado</div>
      <div className="cf-rowside">Real: Permanece</div>
      {cells.slice(0, 2).map((c, i) => <CfCell key={i} c={c} total={total} />)}
      <div className="cf-rowside">Real: Rebaixado</div>
      {cells.slice(2).map((c, i) => <CfCell key={i} c={c} total={total} />)}
    </div>
  );
}
function CfCell({ c, total }) {
  return (
    <div className={`cf-cell ${c.good ? "cf-good" : "cf-bad"}`}
      style={{ opacity: 0.35 + 0.65 * (c.v / total) }}>
      <span className="cf-num">{c.v}</span>
      <span className="cf-lbl">{c.l}</span>
    </div>
  );
}

function BoxRow({ stat, scaleMax, color }) {
  const X = (v) => (v / scaleMax) * 100;
  return (
    <div className="boxrow">
      <div className="box-name">{stat.v}</div>
      <div className="box-track">
        <div className="box-whisker" style={{ left: `${X(stat.min)}%`, width: `${X(stat.max) - X(stat.min)}%`, background: color }} />
        <div className="box-iqr" style={{ left: `${X(stat.q1)}%`, width: `${X(stat.q3) - X(stat.q1)}%`, background: color }} />
        <div className="box-med" style={{ left: `${X(stat.med)}%` }} />
        <div className="box-cap" style={{ left: `${X(stat.min)}%` }} />
        <div className="box-cap" style={{ left: `${X(stat.max)}%` }} />
      </div>
      <div className="box-range">{window.fmtNum(stat.min, 0)}–{window.fmtNum(stat.max, 0)}</div>
    </div>
  );
}

Object.assign(window, { Gauge, VBars, LineChart, RocCurve, CalibCurve, Confusion, BoxRow });
