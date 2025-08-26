import React from "react";
import MiniDonut from "./MiniDonut";
import { Score } from "../types";

type MetricDef = { key: keyof Score; label: string };

type MetricsGridProps = {
  metrics: MetricDef[];
  // mapa 0..1 por métrica (undefined si aún no hay dato)
  scores?: Partial<Record<keyof Score, number>>;
};

export default function MetricsGrid({ metrics, scores }: MetricsGridProps) {
  return (
    <div className="metrics-2col-grid">
      {metrics.map((m) => {
        const v01 = scores?.[m.key];
        const pct = typeof v01 === "number" ? Math.round(Math.max(0, Math.min(1, v01)) * 100) : 0;
        const disabled = !(typeof v01 === "number" && v01 > 0);
        return (
          <div key={m.key as string} className="metrics-2col-grid__item">
            <MiniDonut label={m.label} percent={pct} disabled={disabled} />
          </div>
        );
      })}
    </div>
  );
}
