import type { RequestStatus, RequestPriority } from "../types";
import styles from "./Badge.module.css";

const STATUS_LABELS: Record<RequestStatus, string> = {
  pending: "Pending",
  assigned: "Assigned",
  in_progress: "In Progress",
  approved: "Approved",
  rejected: "Rejected",
  completed: "Completed",
  cancelled: "Cancelled",
};

const PRIORITY_LABELS: Record<RequestPriority, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  urgent: "Urgent",
};

export function StatusBadge({ status }: { status: RequestStatus }) {
  return (
    <span className={`${styles.badge} ${styles[`status_${status}`]}`}>
      {STATUS_LABELS[status]}
    </span>
  );
}

export function PriorityBadge({ priority }: { priority: RequestPriority }) {
  return (
    <span className={`${styles.badge} ${styles[`priority_${priority}`]}`}>
      {PRIORITY_LABELS[priority]}
    </span>
  );
}
