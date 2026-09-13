import { useEffect, useState } from "react";
import { usersApi } from "../api";
import type { User, UserRole } from "../types";
import { Button, LoadingPage, ErrorMessage } from "../components/UI";
import styles from "./AdminUsersPage.module.css";

const ROLES: UserRole[] = ["employee", "manager", "admin"];

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState<string | null>(null);

  useEffect(() => {
    usersApi.list()
      .then(r => setUsers(r.data))
      .catch(() => setError("Failed to load users."))
      .finally(() => setLoading(false));
  }, []);

  async function updateRole(userId: string, role: UserRole) {
    setSaving(userId);
    try {
      const updated = await usersApi.update(userId, { role });
      setUsers(prev => prev.map(u => u.id === userId ? updated.data : u));
    } catch {
      setError("Failed to update role.");
    } finally { setSaving(null); }
  }

  async function toggleActive(user: User) {
    setSaving(user.id);
    try {
      const updated = await usersApi.update(user.id, { is_active: !user.is_active });
      setUsers(prev => prev.map(u => u.id === user.id ? updated.data : u));
    } catch {
      setError("Failed to update user.");
    } finally { setSaving(null); }
  }

  if (loading) return <LoadingPage />;

  return (
    <div>
      <h1 className={styles.title}>User Management</h1>
      {error && <ErrorMessage message={error} />}
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
    </div>
  );
}
