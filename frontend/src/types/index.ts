export type UserRole = "employee" | "manager" | "admin";
export type RequestPriority = "low" | "medium" | "high" | "urgent";
export type RequestStatus =
  | "pending"
  | "assigned"
  | "in_progress"
  | "approved"
  | "rejected"
  | "completed"
  | "cancelled";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  manager_id: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RequestCategory {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
}

export interface WorkflowRequest {
  id: string;
  title: string;
  description: string;
  category_id: string | null;
  requester_id: string;
  assignee_id: string | null;
  priority: RequestPriority;
  status: RequestStatus;
  created_at: string;
  updated_at: string;
  due_date: string | null;
  completed_at: string | null;
}

export interface RequestComment {
  id: string;
  request_id: string;
  author_id: string;
  body: string;
  created_at: string;
}

export interface StatusHistoryEntry {
  id: string;
  request_id: string;
  from_status: RequestStatus | null;
  to_status: RequestStatus;
  changed_by_id: string;
  note: string | null;
  changed_at: string;
}

export interface Notification {
  id: string;
  recipient_id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  previous_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  details: Record<string, unknown> | null;
  created_at: string;
}

export interface DashboardSummary {
  total: number;
  pending: number;
  assigned: number;
  in_progress: number;
  approved: number;
  rejected: number;
  completed: number;
  cancelled: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface RequestFilters {
  search?: string;
  status?: RequestStatus;
  priority?: RequestPriority;
  category_id?: string;
  page?: number;
  page_size?: number;
}
