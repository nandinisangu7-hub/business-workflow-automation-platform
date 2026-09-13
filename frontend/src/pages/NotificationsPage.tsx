import { useEffect, useState } from "react";
import { notificationsApi } from "../api";
import type { Notification } from "../types";
import { Button, LoadingPage, EmptyState, ErrorMessage } from "../components/UI";
import styles from "./NotificationsPage.module.css";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  function load() {
    notificationsApi.list()
      .then(r => setNotifications(r.data))
      .catch(() => setError("Failed to load notifications."))
      .finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, []);

  async function markRead(id: string) {
    await notificationsApi.markRead(id);
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
  }

  async function markAll() {
    await notificationsApi.markAllRead();
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
  }

  if (loading) return <LoadingPage />;
  if (error) return <ErrorMessage message={error} />;

  const unread = notifications.filter(n => !n.is_read).length;

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Notifications {unread > 0 && <span className={styles.badge}>{unread}</span>}</h1>
        {unread > 0 && <Button variant="secondary" size="sm" onClick={markAll}>Mark all read</Button>}
      </div>

      {notifications.length === 0
        ? <EmptyState title="No notifications" message="You're all caught up." />
        : (
          <div className={styles.list}>
            {notifications.map(n => (
              <div key={n.id} className={`${styles.item} ${n.is_read ? styles.read : styles.unread}`}>
                <div className={styles.itemContent}>
                  <p className={styles.itemTitle}>{n.title}</p>
                  <p className={styles.itemMsg}>{n.message}</p>
                  <span className={styles.itemDate}>{new Date(n.created_at).toLocaleString()}</span>
                </div>
                {!n.is_read && (
                  <Button variant="ghost" size="sm" onClick={() => markRead(n.id)}>Mark read</Button>
                )}
              </div>
            ))}
          </div>
        )}
    </div>
  );
}
