import api from "./client";
import type { Notification, AuditLog, DashboardSummary, User } from "../types";

export const notificationsApi = {
  list: () => api.get<Notification[]>("/notifications"),
  unreadCount: () => api.get<{ unread_count: number }>("/notifications/unread-count"),
  markRead: (id: string) => api.patch<Notification>(`/notifications/${id}/read`),
  markAllRead: () => api.post("/notifications/read-all"),
};

export const dashboardApi = {
  summary: () => api.get<DashboardSummary>("/dashboard/summary"),
};

export const auditApi = {
  list: (entity_type?: string, entity_id?: string) =>
    api.get<AuditLog[]>("/audit-logs", { params: { entity_type, entity_id } }),
};

export const usersApi = {
  list: () => api.get<User[]>("/users"),
  get: (id: string) => api.get<User>(`/users/${id}`),
  update: (id: string, data: Partial<{ full_name: string; is_active: boolean; role: string }>) =>
    api.patch<User>(`/users/${id}`, data),
};
