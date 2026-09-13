import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from "react";
import styles from "./UI.module.css";

/* ── Button ─────────────────────────────────────────────────────────── */
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md";
}
export function Button({
  variant = "primary",
  size = "md",
  className = "",
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`${styles.btn} ${styles[`btn_${variant}`]} ${styles[`btn_${size}`]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}

/* ── Input ──────────────────────────────────────────────────────────── */
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}
export function Input({ label, error, id, className = "", ...rest }: InputProps) {
  return (
    <div className={styles.field}>
      {label && <label htmlFor={id} className={styles.label}>{label}</label>}
      <input id={id} className={`${styles.input} ${error ? styles.inputError : ""} ${className}`} {...rest} />
      {error && <span className={styles.fieldError}>{error}</span>}
    </div>
  );
}

/* ── Select ─────────────────────────────────────────────────────────── */
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}
export function Select({ label, error, id, className = "", children, ...rest }: SelectProps) {
  return (
    <div className={styles.field}>
      {label && <label htmlFor={id} className={styles.label}>{label}</label>}
      <select id={id} className={`${styles.input} ${error ? styles.inputError : ""} ${className}`} {...rest}>
        {children}
      </select>
      {error && <span className={styles.fieldError}>{error}</span>}
    </div>
  );
}

/* ── Textarea ───────────────────────────────────────────────────────── */
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}
export function Textarea({ label, error, id, className = "", ...rest }: TextareaProps) {
  return (
    <div className={styles.field}>
      {label && <label htmlFor={id} className={styles.label}>{label}</label>}
      <textarea id={id} className={`${styles.input} ${error ? styles.inputError : ""} ${className}`} rows={4} {...rest} />
      {error && <span className={styles.fieldError}>{error}</span>}
    </div>
  );
}

/* ── Spinner ────────────────────────────────────────────────────────── */
export function Spinner({ size = 24 }: { size?: number }) {
  return (
    <span
      className={styles.spinner}
      style={{ width: size, height: size }}
      role="status"
      aria-label="Loading"
    />
  );
}

/* ── LoadingPage ────────────────────────────────────────────────────── */
export function LoadingPage() {
  return (
    <div className={styles.centred}>
      <Spinner size={40} />
    </div>
  );
}

/* ── EmptyState ─────────────────────────────────────────────────────── */
export function EmptyState({ title, message, action }: { title: string; message?: string; action?: ReactNode }) {
  return (
    <div className={styles.emptyState}>
      <p className={styles.emptyTitle}>{title}</p>
      {message && <p className={styles.emptyMsg}>{message}</p>}
      {action}
    </div>
  );
}

/* ── ErrorMessage ───────────────────────────────────────────────────── */
export function ErrorMessage({ message }: { message: string }) {
  return <div className={styles.errorBox}>{message}</div>;
}

/* ── Card ───────────────────────────────────────────────────────────── */
export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`${styles.card} ${className}`}>{children}</div>;
}
