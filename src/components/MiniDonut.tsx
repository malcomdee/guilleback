import React from "react";
import { DonutChart } from "@carbon/charts-react";

type MiniDonutProps = {
  label: string;
  percent: number; // 0..100
  disabled?: boolean;
  height?: number; // px (default 160)
};

export default function MiniDonut({ label, percent, disabled, height = 160 }: MiniDonutProps) {
  return (
    <div className={`mini-donut ${disabled ? "mini-donut--disabled" : ""}`}>
      <DonutChart
        data={[
          { group: label, value: Math.max(0, Math.min(100, percent)) },
          { group: "Resto", value: Math.max(0, 100 - Math.max(0, Math.min(100, percent))) },
        ]}
        options={{
          title: undefined,
          height: `${height}px`,
          donut: { center: { label: "100" } },
          legend: { alignment: "center" },
          tooltip: { enabled: true },
        }}
      />
      <div className="mini-donut__label">{label}</div>
    </div>
  );
}
