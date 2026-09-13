import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { requestsApi } from "../api/requests";
import type { RequestCategory } from "../types";
import { Button, Input, Select, Textarea, ErrorMessage, Card } from "../components/UI";
import styles from "./NewRequestPage.module.css";

export default function NewRequestPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [categoryId, setCategoryId] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [categories, setCategories] = useState<RequestCategory[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    requestsApi.categories().then(r => setCategories(r.data)).catch(() => {});
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (title.trim().length < 3) { setError("Title must be at least 3 characters."); return; }
    if (description.trim().length < 3) { setError("Description must be at least 3 characters."); return; }
    setError(""); setLoading(true);
    try {
      const req = await requestsApi.create({
        title: title.trim(), description: description.trim(), priority,
        category_id: categoryId || null,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
      });
      navigate(`/requests/${req.data.id}`);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Failed to create request.";
      setError(msg);
    } finally { setLoading(false); }
  }

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>New Request</h1>
      <Card className={styles.card}>
        {error && <ErrorMessage message={error} />}
        <form onSubmit={handleSubmit} className={styles.form}>
          <Input id="title" label="Title" value={title} onChange={e => setTitle(e.target.value)} required placeholder="Brief summary of what you need" />
          <Textarea id="description" label="Description" value={description} onChange={e => setDescription(e.target.value)} required placeholder="Provide full details…" rows={5} />
          <div className={styles.row}>
            <Select id="priority" label="Priority" value={priority} onChange={e => setPriority(e.target.value)}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </Select>
            <Select id="category" label="Category (optional)" value={categoryId} onChange={e => setCategoryId(e.target.value)}>
              <option value="">— None —</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </Select>
          </div>
          <Input id="due_date" label="Due date (optional)" type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} />
          <div className={styles.actions}>
            <Button type="button" variant="secondary" onClick={() => navigate(-1)}>Cancel</Button>
            <Button type="submit" disabled={loading}>{loading ? "Submitting…" : "Submit Request"}</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
