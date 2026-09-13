import api from "./client";
import type {
  WorkflowRequest,
  RequestComment,
  RequestCategory,
  StatusHistoryEntry,
  RequestFilters,
} from "../types";

export const requestsApi = {
  list: (filters: RequestFilters = {}) =>
    api.get<WorkflowRequest[]>("/requests", { params: filters }),

  get: (id: string) => api.get<WorkflowRequest>(`/requests/${id}`),

  create: (data: {
    title: string;
    description: string;
    priority: string;
    category_id?: string | null;
    due_date?: string | null;
  }) => api.post<WorkflowRequest>("/requests", data),

  update: (
    id: string,
    data: Partial<{
      title: string;
      description: string;
      priority: string;
      category_id: string | null;
      due_date: string | null;
    }>
  ) => api.patch<WorkflowRequest>(`/requests/${id}`, data),

  cancel: (id: string) => api.post<WorkflowRequest>(`/requests/${id}/cancel`),

  assign: (id: string, assignee_id: string) =>
    api.post<WorkflowRequest>(`/requests/${id}/assign`, { assignee_id }),

  transition: (id: string, status: string, note?: string) =>
    api.post<WorkflowRequest>(`/requests/${id}/transition`, { status, note }),

  history: (id: string) =>
    api.get<StatusHistoryEntry[]>(`/requests/${id}/history`),

  comments: (id: string) =>
    api.get<RequestComment[]>(`/requests/${id}/comments`),

  addComment: (id: string, body: string) =>
    api.post<RequestComment>(`/requests/${id}/comments`, { body }),

  categories: () => api.get<RequestCategory[]>("/categories"),
};
