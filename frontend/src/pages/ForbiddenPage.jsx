import { Link } from "react-router-dom";

export function ForbiddenPage() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "var(--space-3)" }}>
      <h1 style={{ fontSize: "2rem" }}>Access denied</h1>
      <p style={{ color: "var(--color-ink-muted)" }}>You don't have permission to view this page.</p>
      <Link to="/dashboard" className="btn-primary">Back to dashboard</Link>
    </div>
  );
}
