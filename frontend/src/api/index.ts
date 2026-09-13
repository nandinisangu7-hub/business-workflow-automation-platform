import api from "./client";
import type { Notification, AuditLog, DashboardSummary, User, PaginatedResponse } from "../types";

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
  list: (params: { entity_type?: string; entity_id?: string; page?: number; page_size?: number } = {}) =>
    api.get<PaginatedResponse<AuditLog>>("/audit-logs", { params }),
};

export const usersApi = {
  list: (params: { search?: string; role?: string; page?: number; page_size?: number } = {}) =>
    api.get<PaginatedResponse<User>>("/users", { params }),
  get: (id: string) => api.get<User>(`/users/${id}`),
  update: (id: string, data: Partial<{ full_name: string; is_active: boolean; role: string }>) =>
    api.patch<User>(`/users/${id}`, data),
};
