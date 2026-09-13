import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { notificationsApi } from "../api";
import { useEffect, useState } from "react";
import styles from "./AppLayout.module.css";

const NAV_LINKS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/requests", label: "Requests" },
  { to: "/requests/new", label: "New Request" },
  { to: "/notifications", label: "Notifications" },
  { to: "/profile", label: "Profile" },
];

const ADMIN_LINKS = [
  { to: "/admin/users", label: "Users" },
  { to: "/admin/audit-logs", label: "Audit Logs" },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    notificationsApi.unreadCount()
      .then(r => setUnread(r.data.unread_count))
      .catch(() => {});
    const id = setInterval(() => {
      notificationsApi.unreadCount()
        .then(r => setUnread(r.data.unread_count))
        .catch(() => {});
    }, 30000);
    return () => clearInterval(id);
  }, []);

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>WorkflowPlatform</div>
        <nav className={styles.nav}>
          {NAV_LINKS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `${styles.link} ${isActive ? styles.active : ""}`
              }
            >
              {label}
              {label === "Notifications" && unread > 0 && (
                <span className={styles.badge}>{unread}</span>
              )}
            </NavLink>
          ))}
          {(user?.role === "admin" || user?.role === "manager") && (
            <div className={styles.section}>
              <span className={styles.sectionLabel}>
                {user.role === "admin" ? "Admin" : "Manager"}
              </span>
              {(user.role === "admin" ? ADMIN_LINKS : ADMIN_LINKS.slice(0, 1)).map(
                ({ to, label }) => (
                  <NavLink
                    key={to}
                    to={to}
                    className={({ isActive }) =>
                      `${styles.link} ${isActive ? styles.active : ""}`
                    }
                  >
                    {label}
                  </NavLink>
                )
              )}
            </div>
          )}
        </nav>
        <div className={styles.footer}>
          <span className={styles.userInfo}>
            {user?.full_name}
            <span className={styles.role}>{user?.role}</span>
          </span>
          <button className={styles.logoutBtn} onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}
