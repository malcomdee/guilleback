// src/ResultsTable.tsx
import React from "react";

/* ============== Tipos y constantes ============== */
type Row = {
  ID: number | string;
  NOMBRE: string;
  FECHA: string;              // YYYY-MM-DD
  PREGUNTA: number;
  VEREDICTO: string | null;   // "Correcta" | "Incorrecta" | "Mejorable"
  ANSWER_SIMILARITY: number | string | null;  // 0..100
  ANSWER_RELEVANCE:  number | string | null;  // 0..100
  FAITHFULNESS:      number | string | null;  // 0..100
  CONTEXT_RELEVANCE: number | string | null;  // 0..100
};

const API_BASE = "https://application-33.1zvd1ciw0wl5.us-south.codeengine.appdomain.cloud";
const METRIC_KEY: keyof Row = "ANSWER_SIMILARITY";

/* ============== Utils ============== */
function getCookie(name: string): string | null {
  const target = `${encodeURIComponent(name)}=`;
  const found = document.cookie.split(";").map(c => c.trim()).find(c => c.startsWith(target));
  return found ? decodeURIComponent(found.slice(target.length)) : null;
}
const fmtPct = (x: any) => (x == null || x === "" ? "—" : `${Number(x).toFixed(2)}%`);
const todayISO = () => new Date(Date.now() - new Date().getTimezoneOffset()*60000).toISOString().slice(0,10);
const toNum = (x: any): number => {
  if (x == null || x === "") return NaN;
  const n = typeof x === "string" ? Number(String(x).replace("%","")) : Number(x);
  return Number.isFinite(n) ? n : NaN;
};

/* ============== Estilos base ============== */
const card: React.CSSProperties = {
  borderRadius: 14,
  border: "1px solid #e9edf2",
  boxShadow: "0 1px 2px rgba(16,24,40,.04), 0 4px 10px rgba(16,24,40,.06)",
  background: "#fff", padding: 16,
};
const sectionTitle: React.CSSProperties = {
  margin: "4px 0 10px", fontWeight: 700, fontSize: 14, color: "#1f2937", letterSpacing: ".2px",
};
const chip: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 8px",
  borderRadius: 999, background: "#f2f4f8", fontSize: 12, color: "#4b5563", lineHeight: 1,
};

/* ============== Barras (SVG) con repintado ============== */
type BarDatum = { label: string; value: number; hint?: string };

function PrettyBars({
  title, subtitle, data, chartKey
}: { title: string; subtitle?: React.ReactNode; data: BarDatum[]; chartKey: number; }) {
  const max = Math.max(1, ...data.map(d => d.value));
  const barH = 28, gap = 14, pad = 12;
  const width = 900;
  const height = pad*2 + data.length*barH + (data.length-1)*gap;
  const total = data.reduce((a,b)=>a+b.value,0);

  return (
    <div style={card}>
      <div style={{ display:"flex", justifyContent:"space-between" }}>
        <div>
          <div style={sectionTitle}>{title}</div>
          {subtitle && <div style={{ color:"#6b7280", fontSize:12 }}>{subtitle}</div>}
        </div>
        <span style={chip}><strong style={{ color:"#111827" }}>{total}</strong> total</span>
      </div>

      <svg key={chartKey} viewBox={`0 0 ${width} ${height}`} style={{ width:"100%", height:"auto" }}>
        <defs>
          <linearGradient id="barGrad" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="#4f46e5" />
            <stop offset="100%" stopColor="#2563eb" />
          </linearGradient>
        </defs>

        {data.map((d, i) => {
          const y = pad + i*(barH+gap);
          const w = (d.value / max) * (width - 220);
          return (
            <g key={`${chartKey}-${d.label}`} transform={`translate(0, ${y})`}>
              <foreignObject x={10} y={0} width={140} height={barH}>
                <div style={{
                  display:"flex", alignItems:"center", height:barH, width:140,
                  whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis",
                  fontSize:14, color:"#374151"
                }} title={d.label}>
                  {d.label}
                </div>
              </foreignObject>

              <rect x={160} y={0} width={width-220} height={barH} rx={8} fill="#f3f4f6" />
              <rect x={160} y={0} width={Math.max(4, w)} height={barH} rx={8} fill="url(#barGrad)">
                <animate attributeName="width" from={4} to={Math.max(4, w)} dur="350ms" fill="freeze" />
              </rect>
              <text x={160 + Math.max(4, w) + 10} y={barH/2 + 5} fontSize="12" fill="#111827">{d.value}</text>
              {d.hint && <title>{d.hint}</title>}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/* ============== Top desempeño (solo malcom) ============== */
function TopPerformance({ rows }: { rows: Row[] }) {
  const byName = new Map<string, { correct: number; bucket75100: number }>();
  const inBucket = (v: number) => v >= 75 && v < 100.0001;

  rows.forEach(r => {
    const name = r.NOMBRE || "—";
    const entry = byName.get(name) || { correct: 0, bucket75100: 0 };
    if ((r.VEREDICTO || "").toLowerCase() === "correcta") entry.correct += 1;
    const v = toNum(r[METRIC_KEY]);
    if (Number.isFinite(v) && inBucket(v as number)) entry.bucket75100 += 1;
    byName.set(name, entry);
  });

  const arr = [...byName.entries()].map(([name, v]) => ({ name, ...v }));
  if (!arr.length) return null;

  const maxCorrect = Math.max(...arr.map(a => a.correct));
  const maxBucket  = Math.max(...arr.map(a => a.bucket75100));
  const bestCorrect = arr.filter(a => a.correct === maxCorrect && maxCorrect>0);
  const bestBucket  = arr.filter(a => a.bucket75100 === maxBucket && maxBucket>0);

  return (
    <div style={{ ...card, display:"grid", gap:10 }}>
      <div style={sectionTitle}>Top desempeño</div>
      <div style={{ display:"flex", gap:12, flexWrap:"wrap" }}>
        <div style={{ ...card, padding:12 }}>
          <div style={{ fontSize:12, color:"#6b7280" }}>Más respuestas correctas</div>
          <div style={{ fontWeight:700, marginTop:4 }}>
            {bestCorrect.length ? bestCorrect.map(b => `${b.name} (${b.correct})`).join(", ") : "—"}
          </div>
        </div>
        <div style={{ ...card, padding:12 }}>
          <div style={{ fontSize:12, color:"#6b7280" }}>
            Más respuestas con {String(METRIC_KEY).toLowerCase().replaceAll("_"," ")} 75–100%
          </div>
          <div style={{ fontWeight:700, marginTop:4 }}>
            {bestBucket.length ? bestBucket.map(b => `${b.name} (${b.bucket75100})`).join(", ") : "—"}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============== Acordeón por persona ============== */
function PersonAccordion({ name, rows, defaultOpen = false }: { name: string; rows: Row[]; defaultOpen?: boolean }) {
  // mini resumen
  const correct = rows.filter(r => (r.VEREDICTO || "").toLowerCase() === "correcta").length;
  const bucket75100 = rows.filter(r => {
    const v = toNum(r[METRIC_KEY]);
    return Number.isFinite(v) && (v as number) >= 75 && (v as number) < 100.0001;
  }).length;

  return (
    <details open={defaultOpen} style={{ ...card, padding: 0 }}>
      <summary style={{
        listStyle: "none", cursor: "pointer", padding: "12px 16px",
        display:"flex", alignItems:"center", justifyContent:"space-between"
      }}
      onClick={(e)=>{ /* evita scroll brusco en algunos navegadores */ e.preventDefault(); (e.currentTarget.parentNode as HTMLDetailsElement).open = !(e.currentTarget.parentNode as HTMLDetailsElement).open; }}>
        <div style={{ fontWeight: 700, color: "#111827" }}>{name}</div>
        <div style={{ display:"flex", gap:8 }}>
          <span style={chip}><strong>{rows.length}</strong> filas</span>
          <span style={{ ...chip, background:"#e6fffa", color:"#0f766e", border:"1px solid #99f6e4" }}>
            ✅ {correct}
          </span>
          <span style={{ ...chip, background:"#eef2ff", color:"#4338ca", border:"1px solid #e0e7ff" }}>
            75–100%: {bucket75100}
          </span>
        </div>
      </summary>

      <div style={{ borderTop: "1px solid #eef2f7", padding: 12, overflow: "auto" }}>
        <table style={{ borderCollapse:"collapse", width:"100%" }}>
          <thead>
            <tr style={{ background:"#f9fafb" }}>
              {["ID","Nombre","Fecha","Pregunta","Veredicto","Answer Similarity","Answer Relevance","Faithfulness","Context Relevance"]
                .map(h => (
                  <th key={h} style={{ textAlign:"left", padding:"10px 12px", borderBottom:"1px solid #eef2f7",
                    fontSize:12, color:"#6b7280", fontWeight:700 }}>{h}</th>
                ))}
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={String(r.ID)}>
                {[
                  r.ID, r.NOMBRE, r.FECHA, r.PREGUNTA, r.VEREDICTO || "—",
                  fmtPct(r.ANSWER_SIMILARITY), fmtPct(r.ANSWER_RELEVANCE),
                  fmtPct(r.FAITHFULNESS), fmtPct(r.CONTEXT_RELEVANCE),
                ].map((cell, i) => (
                  <td key={i} style={{ padding:"10px 12px", borderBottom:"1px solid #f3f4f6", fontSize:13, color:"#1f2937" }}>
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

/* ============== Componente principal ============== */
export default function ResultsTable() {
  const cookieName = (getCookie("wx_name") || "").trim();
  const isOwner = cookieName.toLowerCase() === "malcom";

  const [rows, setRows] = React.useState<Row[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [chartKey, setChartKey] = React.useState(0);

  // filtros de consulta al backend
  const [name, setName]   = React.useState<string>(isOwner ? cookieName : cookieName);
  const [from, setFrom]   = React.useState<string>(isOwner ? "" : todayISO());
  const [to,   setTo]     = React.useState<string>(isOwner ? "" : todayISO());
  const [limit, setLimit] = React.useState<number>(50);

  const buildQuery = () => {
    const qs = new URLSearchParams();
    if (isOwner) {
      if (name) qs.set("name", name);
      if (from) qs.set("from", from);
      if (to)   qs.set("to", to);
      qs.set("limit", String(limit || 50));
    } else {
      const viewer = cookieName || "Anon";
      qs.set("name", viewer);
      const hoy = todayISO();
      qs.set("from", hoy); qs.set("to", hoy);
      qs.set("limit", "100");
    }
    return qs;
  };

  const load = async () => {
    try {
      setLoading(true); setError(null);
      const qs = buildQuery();
      const res = await fetch(`${API_BASE}/api/results?${qs.toString()}`, {
        headers: { "X-User-Name": cookieName || "" }
      });
      const data = await res.json();
      if (!res.ok || !data.ok) throw new Error(data?.error || `HTTP ${res.status}`);
      setRows(data.rows || []);
      setChartKey(k => k + 1); // repintar barras
    } catch (e: any) {
      setError(e?.message || String(e));
      setRows([]);
      setChartKey(k => k + 1);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => { load(); }, []);

  // nombres → acordeones
  const groups = React.useMemo(() => {
    const map = new Map<string, Row[]>();
    rows.forEach(r => {
      const k = r.NOMBRE || "—";
      const arr = map.get(k) || [];
      arr.push(r);
      map.set(k, arr);
    });
    return Array.from(map.entries()).sort((a,b)=>a[0].localeCompare(b[0]));
  }, [rows]);

  // ======= Datos globales para gráficas (sobre todo el set consultado) =======
  const verdicts = ["Correcta", "Incorrecta", "Mejorable"];
  const verdictCounts = verdicts.map(v => ({
    label: v,
    value: rows.filter(r => (r.VEREDICTO || "").toLowerCase() === v.toLowerCase()).length
  }));
  const buckets = [
    { label: "0–25%",   min: 0,  max: 25 },
    { label: "25–50%",  min: 25, max: 50 },
    { label: "50–75%",  min: 50, max: 75 },
    { label: "75–100%", min: 75, max: 100.0001 },
  ];
  const metricVals = rows.map(r => toNum(r[METRIC_KEY])).filter(v => Number.isFinite(v)) as number[];
  const bucketCounts = buckets.map(b => ({
    label: b.label,
    value: metricVals.filter(v => v >= b.min && v < b.max).length,
    hint: `${b.min} ≤ valor < ${b.max} (${String(METRIC_KEY).replaceAll("_"," ").toLowerCase()})`,
  }));

  return (
    <section style={{ display:"grid", gap:18 }}>
      <h2 style={{ margin:"10px 0 0", fontSize:30, fontWeight:700 }}>Resultados guardados (Db2)</h2>

      {isOwner && <TopPerformance rows={rows} />}

      <PrettyBars
        title="Respuestas por veredicto"
        subtitle="Conteo de Correcta / Incorrecta / Mejorable"
        data={verdictCounts}
        chartKey={chartKey}
      />
      <PrettyBars
        title={`Distribución de ${String(METRIC_KEY).replaceAll("_"," ").toLowerCase()} (en %)`}
        subtitle="Agrupado por rangos porcentuales"
        data={bucketCounts}
        chartKey={chartKey + 1}
      />

      {/* ====== Filtros + acciones ====== */}
      <div style={{ ...card, display:"flex", gap:12, flexWrap:"wrap", alignItems:"center" }}>
        <div style={{ fontWeight:700, fontSize:14, color:"#1f2937" }}>Filtros</div>
        {isOwner && (
          <>
            <label>
              <span style={{ fontSize:12, color:"#6b7280" }}>Nombre (consulta)</span><br />
              <input value={name} onChange={e => setName(e.target.value)}
                style={{ padding:"8px 10px", border:"1px solid #e5e7eb", borderRadius:8 }} />
            </label>
            <label>
              <span style={{ fontSize:12, color:"#6b7280" }}>Desde</span><br />
              <input type="date" value={from} onChange={e => setFrom(e.target.value)}
                style={{ padding:"8px 10px", border:"1px solid #e5e7eb", borderRadius:8 }} />
            </label>
            <label>
              <span style={{ fontSize:12, color:"#6b7280" }}>Hasta</span><br />
              <input type="date" value={to} onChange={e => setTo(e.target.value)}
                style={{ padding:"8px 10px", border:"1px solid #e5e7eb", borderRadius:8 }} />
            </label>
            <label>
              <span style={{ fontSize:12, color:"#6b7280" }}>Límite</span><br />
              <input type="number" min={1} max={500} value={limit} onChange={e => setLimit(+e.target.value)}
                style={{ width:100, padding:"8px 10px", border:"1px solid #e5e7eb", borderRadius:8 }} />
            </label>
          </>
        )}

        <button onClick={load} disabled={loading}
          style={{ padding:"10px 14px", borderRadius:10, border:"1px solid #3b82f6",
            background: loading ? "linear-gradient(90deg,#a5b4fc,#93c5fd)" : "linear-gradient(90deg,#6366f1,#3b82f6)",
            color:"#fff", fontWeight:600, cursor:"pointer", boxShadow:"0 6px 14px rgba(59,130,246,.25)" }}>
          {loading ? "Cargando…" : "Actualizar"}
        </button>

        <a href={`${API_BASE}/api/results.csv?${buildQuery().toString()}`} target="_blank" rel="noreferrer"
           style={{ ...chip, textDecoration:"none", background:"#eef2ff", color:"#4338ca", border:"1px solid #e0e7ff" }}>
          Descargar CSV
        </a>
      </div>

      {/* ====== Acordeones por persona (compacto) ====== */}
      <div style={{ display:"grid", gap:12 }}>
        {groups.length === 0 && (
          <div style={{ ...card, color:"#6b7280" }}>
            {loading ? "Cargando…" : error ? `Error: ${error}` : "Sin resultados."}
          </div>
        )}
        {groups.map(([person, personRows]) => (
          <PersonAccordion
            key={person}
            name={person}
            rows={personRows}
            defaultOpen={!isOwner} // visitantes: auto-expand su único acordeón
          />
        ))}
      </div>
    </section>
  );
}
