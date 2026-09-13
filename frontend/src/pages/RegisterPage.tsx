import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authApi } from "../api/auth";
import { Button, Input, ErrorMessage } from "../components/UI";
import styles from "./Auth.module.css";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      await authApi.register(email, fullName, password);
      navigate("/login");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Registration failed.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Create account</h1>
        <p className={styles.subtitle}>Business Workflow Automation Platform</p>
        {error && <ErrorMessage message={error} />}
        <form onSubmit={handleSubmit} className={styles.form}>
          <Input id="name" label="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} required autoFocus />
          <Input id="email" label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input id="password" label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button type="submit" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Creating account…" : "Create account"}
          </Button>
        </form>
        <p className={styles.footer}>
          Already have an account?{" "}
          <Link to="/login" className={styles.link}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
