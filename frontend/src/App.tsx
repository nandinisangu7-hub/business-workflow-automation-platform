import { Routes, Route, Navigate } from "react-router-dom";
import RequireAuth from "./routes/RequireAuth";
import AppLayout from "./layouts/AppLayout";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import RequestsPage from "./pages/RequestsPage";
import NewRequestPage from "./pages/NewRequestPage";
import RequestDetailPage from "./pages/RequestDetailPage";
import NotificationsPage from "./pages/NotificationsPage";
import ProfilePage from "./pages/ProfilePage";
import AdminUsersPage from "./pages/AdminUsersPage";
import AuditLogsPage from "./pages/AuditLogsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/requests" element={<RequestsPage />} />
          <Route path="/requests/new" element={<NewRequestPage />} />
          <Route path="/requests/:id" element={<RequestDetailPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/profile" element={<ProfilePage />} />

          <Route element={<RequireAuth allowedRoles={["admin"]} />}>
            <Route path="/admin/users" element={<AdminUsersPage />} />
            <Route path="/audit" element={<AuditLogsPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
