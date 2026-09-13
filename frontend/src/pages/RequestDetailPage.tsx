import { useEffect, useState, type FormEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { requestsApi } from "../api/requests";
import { usersApi } from "../api";
import { useAuth } from "../context/AuthContext";
import type { WorkflowRequest, RequestComment, StatusHistoryEntry, User } from "../types";
import { StatusBadge, PriorityBadge } from "../components/Badge";
import { Button, Textarea, ErrorMessage, LoadingPage, Card } from "../components/UI";
import styles from "./RequestDetailPage.module.css";

function fmt(iso: string) { return new Date(iso).toLocaleString(); }

function Timeline({ history }: { history: StatusHistoryEntry[] }) {
  return (
    <div className={styles.timeline}>
      {history.map((h, i) => (
        <div key={h.id} className={styles.timelineItem}>
          <div className={styles.timelineDot} />
          {i < history.length - 1 && <div className={styles.timelineLine} />}
          <div className={styles.timelineContent}>
            <span className={styles.timelineStatus}>
              {h.from_status ? `${h.from_status.replace("_"," ")} → ` : ""}{h.to_status.replace("_"," ")}
            </span>
            {h.note && <span className={styles.timelineNote}> — {h.note}</span>}
            <span className={styles.timelineDate}>{fmt(h.changed_at)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function RequestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [request, setRequest] = useState<WorkflowRequest | null>(null);
  const [comments, setComments] = useState<RequestComment[]>([]);
  const [history, setHistory] = useState<StatusHistoryEntry[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [commentBody, setCommentBody] = useState("");
  const [assigneeId, setAssigneeId] = useState("");
  const [transitionNote, setTransitionNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");

  const isManagerOrAdmin = user?.role === "manager" || user?.role === "admin";
  const isOwner = request?.requester_id === user?.id;

  useEffect(() => {
    if (!id) return;
    Promise.all([
      requestsApi.get(id),
      requestsApi.comments(id),
      requestsApi.history(id),
    ]).then(([r, c, h]) => {
      setRequest(r.data);
      setComments(c.data);
      setHistory(h.data);
    }).catch(() => setError("Failed to load request."))
      .finally(() => setLoading(false));

    if (isManagerOrAdmin) {
      usersApi.list().then(r => setUsers(r.data)).catch(() => {});
    }
  }, [id, isManagerOrAdmin]);

  async function doAction(fn: () => Promise<unknown>) {
    setActionError(""); setActionLoading(true);
    try {
      await fn();
      const [r, c, h] = await Promise.all([
        requestsApi.get(id!), requestsApi.comments(id!), requestsApi.history(id!),
      ]);
      setRequest(r.data); setComments(c.data); setHistory(h.data);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Action failed.";
      setActionError(msg);
    } finally { setActionLoading(false); }
  }

  async function submitComment(e: FormEvent) {
    e.preventDefault();
    if (!commentBody.trim()) return;
    await doAction(async () => { await requestsApi.addComment(id!, commentBody.trim()); setCommentBody(""); });
  }

  if (loading) return <LoadingPage />;
  if (error) return <ErrorMessage message={error} />;
  if (!request) return null;

  return (
    <div className={styles.page}>
      <button className={styles.back} onClick={() => navigate(-1)}>← Back</button>

      <div className={styles.topRow}>
        <div>
          <h1 className={styles.title}>{request.title}</h1>
          <div className={styles.badges}>
            <StatusBadge status={request.status} />
            <PriorityBadge priority={request.priority} />
          </div>
        </div>
      </div>

      {actionError && <ErrorMessage message={actionError} />}

      <div className={styles.grid}>
        {/* Left column */}
        <div className={styles.left}>
          <Card>
            <h2 className={styles.sectionTitle}>Description</h2>
            <p className={styles.description}>{request.description}</p>
          </Card>

          {/* Workflow actions */}
          {(isManagerOrAdmin || isOwner) && (
            <Card>
              <h2 className={styles.sectionTitle}>Actions</h2>
              <div className={styles.actionGroup}>
                {isManagerOrAdmin && request.status === "pending" && (
                  <div className={styles.assignRow}>
                    <select className={styles.select} value={assigneeId} onChange={e => setAssigneeId(e.target.value)}>
                      <option value="">Select assignee…</option>
                      {users.map(u => <option key={u.id} value={u.id}>{u.full_name}</option>)}
                    </select>
                    <Button size="sm" disabled={!assigneeId || actionLoading}
                      onClick={() => doAction(() => requestsApi.assign(id!, assigneeId))}>
                      Assign
                    </Button>
                  </div>
                )}
                {isManagerOrAdmin && request.status === "assigned" && (
                  <Button size="sm" disabled={actionLoading}
                    onClick={() => doAction(() => requestsApi.transition(id!, "in_progress"))}>
                    Start Work
                  </Button>
                )}
                {isManagerOrAdmin && request.status === "in_progress" && (
                  <div className={styles.approveRow}>
                    <input className={styles.noteInput} placeholder="Optional note…" value={transitionNote}
                      onChange={e => setTransitionNote(e.target.value)} />
                    <Button size="sm" disabled={actionLoading}
                      onClick={() => doAction(() => requestsApi.transition(id!, "approved", transitionNote))}>
                      Approve
                    </Button>
                    <Button size="sm" variant="danger" disabled={actionLoading}
                      onClick={() => doAction(() => requestsApi.transition(id!, "rejected", transitionNote))}>
                      Reject
                    </Button>
                  </div>
                )}
                {isManagerOrAdmin && request.status === "approved" && (
                  <Button size="sm" disabled={actionLoading}
                    onClick={() => doAction(() => requestsApi.transition(id!, "completed"))}>
                    Mark Completed
                  </Button>
                )}
                {isOwner && request.status === "pending" && (
                  <Button size="sm" variant="danger" disabled={actionLoading}
                    onClick={() => doAction(() => requestsApi.cancel(id!))}>
                    Cancel Request
                  </Button>
                )}
              </div>
            </Card>
          )}

          {/* Comments */}
          <Card>
            <h2 className={styles.sectionTitle}>Comments ({comments.length})</h2>
            {comments.length === 0 && <p className={styles.noComments}>No comments yet.</p>}
            {comments.map(c => (
              <div key={c.id} className={styles.comment}>
                <div className={styles.commentMeta}>{fmt(c.created_at)}</div>
                <p className={styles.commentBody}>{c.body}</p>
              </div>
            ))}
            <form onSubmit={submitComment} className={styles.commentForm}>
              <Textarea value={commentBody} onChange={e => setCommentBody(e.target.value)}
                placeholder="Add a comment…" rows={3} />
              <Button type="submit" size="sm" disabled={!commentBody.trim() || actionLoading}>
                Post Comment
              </Button>
            </form>
          </Card>
        </div>

        {/* Right column */}
        <div className={styles.right}>
          <Card>
            <h2 className={styles.sectionTitle}>Details</h2>
            <dl className={styles.details}>
              <dt>Status</dt><dd><StatusBadge status={request.status} /></dd>
              <dt>Priority</dt><dd><PriorityBadge priority={request.priority} /></dd>
              <dt>Created</dt><dd>{fmt(request.created_at)}</dd>
              <dt>Updated</dt><dd>{fmt(request.updated_at)}</dd>
              {request.due_date && <><dt>Due</dt><dd>{fmt(request.due_date)}</dd></>}
              {request.completed_at && <><dt>Completed</dt><dd>{fmt(request.completed_at)}</dd></>}
            </dl>
          </Card>

          <Card>
            <h2 className={styles.sectionTitle}>Status Timeline</h2>
            {history.length === 0
              ? <p className={styles.noComments}>No history yet.</p>
              : <Timeline history={history} />}
          </Card>
        </div>
      </div>
    </div>
  );
}
