import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "var(--space-3)" }}>
      <h1 style={{ fontSize: "2rem" }}>Page not found</h1>
      <p style={{ color: "var(--color-ink-muted)" }}>The page you're looking for doesn't exist.</p>
      <Link to="/dashboard" className="btn-primary">Back to dashboard</Link>
    </div>
  );
}
