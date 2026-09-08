export function EmptyState({ title, description, action }) {
  return (
    <div className="card" style={{ padding: "var(--space-7)", textAlign: "center" }}>
      <h3 style={{ marginBottom: "var(--space-2)" }}>{title}</h3>
      {description && (
        <p style={{ color: "var(--color-ink-muted)", marginBottom: "var(--space-4)" }}>
          {description}
        </p>
      )}
      {action}
    </div>
  );
}
