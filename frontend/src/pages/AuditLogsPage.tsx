import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { auditApi } from "../api";
import type { AuditLog, PaginatedResponse } from "../types";
import { LoadingPage, ErrorMessage, EmptyState, Button, Select } from "../components/UI";
import styles from "./AuditLogsPage.module.css";

const ENTITY_TYPES = ["request", "user", "category"];

export default function AuditLogsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState<PaginatedResponse<AuditLog> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const entityType = searchParams.get("entity_type") ?? "";
  const page = parseInt(searchParams.get("page") ?? "1", 10);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    auditApi
      .list({ entity_type: entityType || undefined, page, page_size: 50 })
      .then(r => setData(r.data))
      .catch(() => setError("Failed to load audit logs."))
      .finally(() => setLoading(false));
  }, [entityType, page]);

  useEffect(() => { load(); }, [load]);

  function setParam(key: string, value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value); else next.delete(key);
    next.delete("page");
    setSearchParams(next);
  }

  function setPage(p: number) {
    const next = new URLSearchParams(searchParams);
    next.set("page", String(p));
    setSearchParams(next);
  }

  return (
    <div>
      <h1 className={styles.title}>Audit Logs</h1>

      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem" }}>
        <Select value={entityType} onChange={e => setParam("entity_type", e.target.value)} style={{ maxWidth: 160 }}>
          <option value="">All entities</option>
          {ENTITY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </Select>
      </div>

      {error && <ErrorMessage message={error} />}
      {loading && <LoadingPage />}

      {!loading && !error && data && (
        <>
          {data.items.length === 0
            ? <EmptyState title="No audit logs found" />
            : (
              <div className={styles.tableWrap}>
                <table className={styles.table}>
                  <thead>
                    <tr><th>Action</th><th>Entity</th><th>Entity ID</th><th>Timestamp</th></tr>
                  </thead>
                  <tbody>
                    {data.items.map(l => (
                      <tr key={l.id}>
                        <td><span className={styles.action}>{l.action.replace(/_/g, " ")}</span></td>
                        <td className={styles.entity}>{l.entity_type}</td>
                        <td className={styles.id}>{l.entity_id.slice(0, 8)}…</td>
                        <td className={styles.date}>{new Date(l.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

          {data.total_pages > 1 && (
            <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", marginTop: "1rem" }}>
              <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button>
              <span>Page {data.page} of {data.total_pages} ({data.total} total)</span>
              <Button variant="secondary" size="sm" disabled={page >= data.total_pages} onClick={() => setPage(page + 1)}>Next</Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
