import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Button, Input, ErrorMessage } from "../components/UI";
import styles from "./Auth.module.css";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Login failed. Check your credentials.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Sign in</h1>
        <p className={styles.subtitle}>Business Workflow Automation Platform</p>
        {error && <ErrorMessage message={error} />}
        <form onSubmit={handleSubmit} className={styles.form}>
          <Input
            id="email"
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
          />
          <Input
            id="password"
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <Button type="submit" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Signing in…" : "Sign in"}
          </Button>
        </form>
        <p className={styles.footer}>
          No account?{" "}
          <Link to="/register" className={styles.link}>
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
