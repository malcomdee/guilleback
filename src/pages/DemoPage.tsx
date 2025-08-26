import React from "react";
import GovernanceDemo from "../GovernanceDemo";
import { getCookie } from "../utils/cookies";

export default function DemoPage() {
  const name = getCookie("wx_name") || "";

  return (
    <div className="ibm-shell">
      <header className="ibm-header">
        <span className="ibm-header__title">IBM Governance Demo</span>
        <div style={{ flex: 1 }} />
        {name ? <span style={{ opacity: 0.8 }}>Hola, {name}</span> : null}
      </header>

      <main className="ibm-container">
        <GovernanceDemo />
      </main>
    </div>
  );
}
