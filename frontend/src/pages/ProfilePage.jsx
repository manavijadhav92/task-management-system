import { useAuth } from "../hooks/useAuth";

export function ProfilePage() {
  const { user } = useAuth();

  return (
    <div style={{ maxWidth: 420 }}>
      <h1 style={{ fontSize: "1.4rem", marginBottom: "var(--space-5)" }}>Profile</h1>
      <div className="card" style={{ padding: "var(--space-6)" }}>
        <dl className="task-meta" style={{ gridTemplateColumns: "1fr" }}>
          <div><dt>Name</dt><dd>{user?.name}</dd></div>
          <div><dt>Email</dt><dd>{user?.email}</dd></div>
        </dl>
      </div>
    </div>
  );
}
