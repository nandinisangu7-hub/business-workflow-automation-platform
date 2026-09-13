import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { usersApi } from "../api";
import type { User, UserRole, PaginatedResponse } from "../types";
import { Button, Input, Select, LoadingPage, ErrorMessage } from "../components/UI";
import styles from "./AdminUsersPage.module.css";

const ROLES: UserRole[] = ["employee", "manager", "admin"];

export default function AdminUsersPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState<PaginatedResponse<User> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState<string | null>(null);

  const search = searchParams.get("search") ?? "";
  const role = (searchParams.get("role") ?? "") as UserRole | "";
  const page = parseInt(searchParams.get("page") ?? "1", 10);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    usersApi
      .list({ search: search || undefined, role: role || undefined, page, page_size: 50 })
      .then(r => setData(r.data))
      .catch(() => setError("Failed to load users."))
      .finally(() => setLoading(false));
  }, [search, role, page]);

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

  async function updateRole(userId: string, newRole: UserRole) {
    setSaving(userId);
    try {
      const updated = await usersApi.update(userId, { role: newRole });
      setData(prev => prev ? { ...prev, items: prev.items.map(u => u.id === userId ? updated.data : u) } : prev);
    } catch {
      setError("Failed to update role.");
    } finally { setSaving(null); }
  }

  async function toggleActive(user: User) {
    setSaving(user.id);
    try {
      const updated = await usersApi.update(user.id, { is_active: !user.is_active });
      setData(prev => prev ? { ...prev, items: prev.items.map(u => u.id === user.id ? updated.data : u) } : prev);
    } catch {
      setError("Failed to update user.");
    } finally { setSaving(null); }
  }

  const users = data?.items ?? [];

  return (
    <div>
      <h1 className={styles.title}>User Management</h1>
      {error && <ErrorMessage message={error} />}

      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem" }}>
        <Input
          placeholder="Search name or email…"
          value={search}
          onChange={e => setParam("search", e.target.value)}
          style={{ maxWidth: 240 }}
        />
        <Select value={role} onChange={e => setParam("role", e.target.value)} style={{ maxWidth: 140 }}>
          <option value="">All roles</option>
          {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
        </Select>
      </div>

      {loading && <LoadingPage />}

      {!loading && (
        <>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td className={styles.name}>{u.full_name}</td>
                    <td className={styles.email}>{u.email}</td>
                    <td>
                      <select
                        className={styles.roleSelect}
                        value={u.role}
                        disabled={saving === u.id}
                        onChange={e => updateRole(u.id, e.target.value as UserRole)}
                      >
                        {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                      </select>
                    </td>
                    <td>
                      <span className={u.is_active ? styles.active : styles.inactive}>
                        {u.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td>
                      <Button
                        size="sm"
                        variant={u.is_active ? "danger" : "secondary"}
                        disabled={saving === u.id}
                        onClick={() => toggleActive(u)}
                      >
                        {u.is_active ? "Deactivate" : "Activate"}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data && data.total_pages > 1 && (
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
