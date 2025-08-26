import React from "react";
import { InlineLoading } from "@carbon/react";

type ActiveBarProps = {
  text?: string;
  loading?: boolean;
  error?: string | null;
};

export default function ActiveBar({ text, loading, error }: ActiveBarProps) {
  return (
    <div className="gov-activebar">
      <div className="gov-active-text">
        {text ? <span className="gov-ellipsis">{text}</span> : <span className="gov-ellipsis">Selecciona un ejemplo.</span>}
      </div>
      {loading && <InlineLoading description="Evaluando…" />}
      {error && <div className="gov-error">{error}</div>}
    </div>
  );
}
