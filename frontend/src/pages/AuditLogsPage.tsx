import { useEffect, useState } from "react";
import { auditApi } from "../api";
import type { AuditLog } from "../types";
import { LoadingPage, ErrorMessage, EmptyState } from "../components/UI";
import styles from "./AuditLogsPage.module.css";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    auditApi.list()
      .then(r => setLogs(r.data))
      .catch(() => setError("Failed to load audit logs."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingPage />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <h1 className={styles.title}>Audit Logs</h1>
      {logs.length === 0
        ? <EmptyState title="No audit logs yet" />
        : (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr><th>Action</th><th>Entity</th><th>Entity ID</th><th>Timestamp</th></tr>
              </thead>
              <tbody>
                {logs.map(l => (
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
    </div>
  );
}
