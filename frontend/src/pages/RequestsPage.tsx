import { useEffect, useState, useCallback } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { requestsApi } from "../api/requests";
import type { WorkflowRequest, RequestStatus, RequestPriority, PaginatedResponse } from "../types";
import { StatusBadge, PriorityBadge } from "../components/Badge";
import { Button, Input, Select, LoadingPage, EmptyState, ErrorMessage } from "../components/UI";
import styles from "./RequestsPage.module.css";

const STATUSES: RequestStatus[] = ["pending","assigned","in_progress","approved","rejected","completed","cancelled"];
const PRIORITIES: RequestPriority[] = ["low","medium","high","urgent"];

export default function RequestsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState<PaginatedResponse<WorkflowRequest> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const search = searchParams.get("search") ?? "";
  const status = (searchParams.get("status") ?? "") as RequestStatus | "";
  const priority = (searchParams.get("priority") ?? "") as RequestPriority | "";
  const page = parseInt(searchParams.get("page") ?? "1", 10);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    requestsApi
      .list({ search: search || undefined, status: status || undefined, priority: priority || undefined, page, page_size: 20 })
      .then(r => setData(r.data as unknown as PaginatedResponse<WorkflowRequest>))
      .catch(() => setError("Failed to load requests."))
      .finally(() => setLoading(false));
  }, [search, status, priority, page]);

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
      <div className={styles.header}>
        <h1 className={styles.title}>Requests</h1>
        <Link to="/requests/new" className={styles.newBtn}>+ New Request</Link>
      </div>

      <div className={styles.filters}>
        <Input placeholder="Search title or description…" value={search}
          onChange={e => setParam("search", e.target.value)} style={{ maxWidth: 280 }} />
        <Select value={status} onChange={e => setParam("status", e.target.value)} style={{ maxWidth: 160 }}>
          <option value="">All statuses</option>
          {STATUSES.map(s => <option key={s} value={s}>{s.replace("_"," ")}</option>)}
        </Select>
        <Select value={priority} onChange={e => setParam("priority", e.target.value)} style={{ maxWidth: 140 }}>
          <option value="">All priorities</option>
          {PRIORITIES.map(p => <option key={p} value={p}>{p}</option>)}
        </Select>
      </div>

      {error && <ErrorMessage message={error} />}
      {loading && <LoadingPage />}

      {!loading && !error && data && (
        <>
          {data.items.length === 0 ? (
            <EmptyState title="No requests found" message="Try adjusting your filters or create a new request." />
          ) : (
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map(req => (
                    <tr key={req.id}>
                      <td className={styles.titleCell}>
                        <Link to={`/requests/${req.id}`} className={styles.reqLink}>{req.title}</Link>
                      </td>
                      <td><PriorityBadge priority={req.priority} /></td>
                      <td><StatusBadge status={req.status} /></td>
                      <td className={styles.date}>{new Date(req.created_at).toLocaleDateString()}</td>
                      <td>
                        <Link to={`/requests/${req.id}`}>
                          <Button variant="ghost" size="sm">View</Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {data.total_pages > 1 && (
            <div className={styles.pagination}>
              <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button>
              <span className={styles.pageInfo}>Page {data.page} of {data.total_pages} ({data.total} total)</span>
              <Button variant="secondary" size="sm" disabled={page >= data.total_pages} onClick={() => setPage(page + 1)}>Next</Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
