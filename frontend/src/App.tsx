import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
  service: string;
  environment: string;
};

/**
 * Phase 1 placeholder.
 *
 * This is deliberately NOT a dashboard yet — that's Phase 9. Its only job
 * right now is to prove the frontend can reach the backend over HTTP
 * through the Vite dev proxy, which is the thing most likely to be
 * silently broken (wrong port, CORS misconfig, backend not running) and
 * therefore worth verifying before any real UI is built on top of it.
 */
export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/health")
      .then((res) => {
        if (!res.ok) throw new Error(`Backend responded with ${res.status}`);
        return res.json() as Promise<HealthResponse>;
      })
      .then(setHealth)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "2rem", maxWidth: 640 }}>
      <h1>Business Workflow Automation Platform</h1>
      <p>Phase 1 scaffold — architecture, backend skeleton, frontend skeleton.</p>

      <section style={{ marginTop: "1.5rem" }}>
        <h2 style={{ fontSize: "1rem", textTransform: "none" }}>Backend connectivity</h2>
        {error && <p style={{ color: "#b91c1c" }}>Could not reach backend: {error}</p>}
        {!error && !health && <p>Checking backend…</p>}
        {health && (
          <ul>
            <li>Status: {health.status}</li>
            <li>Service: {health.service}</li>
            <li>Environment: {health.environment}</li>
          </ul>
        )}
      </section>
    </main>
  );
}
