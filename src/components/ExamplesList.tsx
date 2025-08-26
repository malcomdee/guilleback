import React from "react";
import { Button } from "@carbon/react";

export type GovExample = {
  id: string;
  text: string;
  hint?: string;
};

type ExamplesListProps = {
  examples: GovExample[];
  activeId?: string | null;
  loadingId?: string | null;
  onClick: (ex: GovExample) => void;
};

export default function ExamplesList({ examples, activeId, loadingId, onClick }: ExamplesListProps) {
  return (
    <div className="examples-list">
      {examples.map((ex) => (
        <Button
          key={ex.id}
          size="sm"
          kind={activeId === ex.id ? "primary" : "secondary"}
          onClick={() => onClick(ex)}
          disabled={loadingId === ex.id}
          className="example-btn"
          title={ex.hint}
        >
          {ex.text}
          {ex.hint ? <span className="example-hint"> · {ex.hint}</span> : null}
        </Button>
      ))}
    </div>
  );
}
