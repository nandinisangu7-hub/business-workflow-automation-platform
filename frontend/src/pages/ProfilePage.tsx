import { useAuth } from "../context/AuthContext";
import { Card } from "../components/UI";
import styles from "./ProfilePage.module.css";

export default function ProfilePage() {
  const { user } = useAuth();
  if (!user) return null;
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Profile</h1>
      <Card className={styles.card}>
        <div className={styles.avatar}>{user.full_name.charAt(0).toUpperCase()}</div>
        <dl className={styles.details}>
          <dt>Full name</dt><dd>{user.full_name}</dd>
          <dt>Email</dt><dd>{user.email}</dd>
          <dt>Role</dt><dd className={styles.role}>{user.role}</dd>
          <dt>Account status</dt><dd>{user.is_active ? "Active" : "Inactive"}</dd>
          <dt>Member since</dt><dd>{new Date(user.created_at).toLocaleDateString()}</dd>
        </dl>
      </Card>
    </div>
  );
}
