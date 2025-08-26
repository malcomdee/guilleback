import React, { useEffect, useState } from "react";
import { Button, Form, Stack, TextInput } from "@carbon/react";
import { useNavigate } from "react-router-dom";

function setCookie(name: string, value: string, days = 180) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}
function getCookie(name: string): string | null {
  const target = `${encodeURIComponent(name)}=`;
  const found = document.cookie
    .split(";")
    .map((c) => c.trim())
    .find((c) => c.startsWith(target));
  return found ? decodeURIComponent(found.slice(target.length)) : null;
}

export default function WelcomePage() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [err, setErr] = useState<string | null>(null);

  // Si ya hay cookie, pasa directo a /app
  useEffect(() => {
    const saved = getCookie("wx_name");
    if (saved) navigate("/app", { replace: true });
  }, [navigate]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const n = name.trim();
    if (!n) {
      setErr("Por favor, ingresa tu nombre.");
      return;
    }
    setCookie("wx_name", n);
    navigate("/app", { replace: true }); // 👈 cambia la URL a /app (App.tsx)
  };

  return (
    <div className="ibm-shell">
      <header className="ibm-header">
        <span className="ibm-header__title">IBM Governance Demo</span>
      </header>

      <main className="ibm-container">
        <div className="welcome-wrap">
          <div className="ibm-card welcome-card">
            <Form onSubmit={handleSubmit}>
              <Stack gap={5}>
                <header>
                  <h2 style={{ margin: 0 }}>Bienvenido</h2>
                  <p style={{ margin: "6px 0 0", color: "var(--cds-text-secondary)" }}>
                    Ingresa tu nombre para continuar.
                  </p>
                </header>

                <TextInput
                  id="username"
                  labelText="Tu nombre"
                  placeholder="Ej.: Malcom"
                  value={name}
                  onChange={(e) => setName(e.currentTarget.value)}
                  invalid={!!err}
                  invalidText={err || ""}
                />

                <div className="ibm-actions">
                  <Button type="submit" kind="primary">Continuar</Button>
                </div>
              </Stack>
            </Form>
          </div>
        </div>
      </main>
    </div>
  );
}
