export function ErrorState({ message, onRetry }) {
  return (
    <div className="card" style={{ padding: "var(--space-5)", borderColor: "var(--color-danger)" }}>
      <p style={{ color: "var(--color-danger)", marginBottom: onRetry ? "var(--space-3)" : 0 }}>
        {message || "Something went wrong."}
      </p>
      {onRetry && (
        <button type="button" className="btn-secondary" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}
