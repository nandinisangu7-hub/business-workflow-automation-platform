import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { dashboardApi } from "../api";
import { useAuth } from "../context/AuthContext";
import type { DashboardSummary } from "../types";
import { LoadingPage, ErrorMessage, Card } from "../components/UI";
import styles from "./DashboardPage.module.css";

interface StatCardProps {
  label: string;
  value: number;
  color: string;
  to?: string;
}

function StatCard({ label, value, color, to }: StatCardProps) {
  const inner = (
    <div className={styles.statCard} style={{ borderTopColor: color }}>
      <span className={styles.statValue}>{value}</span>
      <span className={styles.statLabel}>{label}</span>
    </div>
  );
  return to ? <Link to={to} className={styles.statLink}>{inner}</Link> : inner;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    dashboardApi.summary()
      .then(r => setSummary(r.data))
      .catch(() => setError("Failed to load dashboard data."));
  }, []);

  if (error) return <ErrorMessage message={error} />;
  if (!summary) return <LoadingPage />;

  return (
    <div>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Dashboard</h1>
          <p className={styles.subtitle}>Welcome back, {user?.full_name}</p>
        </div>
        <Link to="/requests/new" className={styles.newBtn}>+ New Request</Link>
      </div>

      <div className={styles.grid}>
        <StatCard label="Total" value={summary.total} color="#6366f1" to="/requests" />
        <StatCard label="Pending" value={summary.pending} color="#f59e0b" to="/requests?status=pending" />
        <StatCard label="Assigned" value={summary.assigned} color="#3b82f6" to="/requests?status=assigned" />
        <StatCard label="In Progress" value={summary.in_progress} color="#8b5cf6" to="/requests?status=in_progress" />
        <StatCard label="Approved" value={summary.approved} color="#10b981" to="/requests?status=approved" />
        <StatCard label="Rejected" value={summary.rejected} color="#ef4444" to="/requests?status=rejected" />
        <StatCard label="Completed" value={summary.completed} color="#059669" to="/requests?status=completed" />
        <StatCard label="Cancelled" value={summary.cancelled} color="#9ca3af" to="/requests?status=cancelled" />
      </div>

      <Card className={styles.quickActions}>
        <h2 className={styles.sectionTitle}>Quick actions</h2>
        <div className={styles.actions}>
          <Link to="/requests/new" className={styles.action}>Submit a request</Link>
          <Link to="/requests" className={styles.action}>View all requests</Link>
          <Link to="/notifications" className={styles.action}>Notifications</Link>
          {(user?.role === "manager" || user?.role === "admin") && (
            <Link to="/requests?status=pending" className={styles.action}>Pending requests</Link>
          )}
        </div>
      </Card>
    </div>
  );
}
