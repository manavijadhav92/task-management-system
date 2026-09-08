import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { taskService } from "../services/taskService";
import { extractErrorMessage } from "../services/api";
import { Spinner } from "../components/ui/Spinner";
import { ErrorState } from "../components/ui/ErrorState";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { StatusBadge } from "../components/tasks/StatusBadge";
import { PriorityBadge } from "../components/tasks/PriorityBadge";
import { formatDate } from "../utils/formatDate";

export function TaskDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const { data: task, isLoading, error, refetch } = useFetch(async () => {
    const { data } = await taskService.get(id);
    return data.data;
  }, [id]);

  if (isLoading) return <Spinner label="Loading task..." />;
  if (error) return <ErrorState message={extractErrorMessage(error)} onRetry={refetch} />;

  const handleDelete = async () => {
    try {
      await taskService.remove(id);
      navigate("/tasks");
    } catch (err) {
      setDeleteError(extractErrorMessage(err));
      setConfirmOpen(false);
    }
  };

  return (
    <div style={{ maxWidth: 640 }}>
      <Link to="/tasks" className="btn-text" style={{ display: "inline-block", marginBottom: "var(--space-4)" }}>
        &larr; Back to tasks
      </Link>

      <div className="card" style={{ padding: "var(--space-6)" }}>
        <h1 style={{ fontSize: "1.4rem", marginBottom: "var(--space-3)" }}>{task.title}</h1>
        <div style={{ display: "flex", gap: "var(--space-4)", marginBottom: "var(--space-5)" }}>
          <StatusBadge status={task.status} />
          <PriorityBadge priority={task.priority} />
        </div>

        {task.description && (
          <p style={{ color: "var(--color-ink-muted)", marginBottom: "var(--space-5)", whiteSpace: "pre-wrap" }}>
            {task.description}
          </p>
        )}

        <dl className="task-meta">
          <div><dt>Due date</dt><dd className="mono">{formatDate(task.due_date)}</dd></div>
          <div><dt>Created</dt><dd className="mono">{formatDate(task.created_at)}</dd></div>
          <div><dt>Last updated</dt><dd className="mono">{formatDate(task.updated_at)}</dd></div>
          {task.assigned_to && <div><dt>Assigned to</dt><dd className="mono">{task.assigned_to}</dd></div>}
        </dl>

        {deleteError && <ErrorState message={deleteError} />}

        <div style={{ display: "flex", gap: "var(--space-3)", marginTop: "var(--space-5)" }}>
          <Link to={`/tasks/${id}/edit`} className="btn-secondary">Edit</Link>
          <button type="button" className="btn-danger" onClick={() => setConfirmOpen(true)}>Delete</button>
        </div>
      </div>

      <ConfirmDialog
        open={confirmOpen}
        title={`Delete "${task.title}"?`}
        description="This can't be undone."
        confirmLabel="Delete"
        onCancel={() => setConfirmOpen(false)}
        onConfirm={handleDelete}
      />
    </div>
  );
}
