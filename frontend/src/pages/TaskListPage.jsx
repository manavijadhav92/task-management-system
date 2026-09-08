import { useState } from "react";
import { Link } from "react-router-dom";
import { useTasks } from "../hooks/useTasks";
import { TaskFilters } from "../components/tasks/TaskFilters";
import { TaskRow } from "../components/tasks/TaskRow";
import { Pagination } from "../components/ui/Pagination";
import { Spinner } from "../components/ui/Spinner";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { extractErrorMessage } from "../services/api";

export function TaskListPage() {
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleteError, setDeleteError] = useState("");

  const {
    filters,
    setFilters,
    page,
    setPage,
    tasks,
    numPages,
    isLoading,
    error,
    refetch,
    changeStatus,
    removeTask,
  } = useTasks();

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "var(--space-5)" }}>
        <h1 style={{ fontSize: "1.4rem" }}>Tasks</h1>
        <Link to="/tasks/new" className="btn-primary">New task</Link>
      </div>

      <TaskFilters filters={filters} onChange={setFilters} />

      {isLoading && <Spinner label="Loading tasks..." />}

      {!isLoading && error && <ErrorState message={error} onRetry={refetch} />}

      {!isLoading && !error && tasks.length === 0 && (
        <EmptyState
          title="No tasks found"
          description="Try adjusting your filters, or create a new task to get started."
          action={<Link to="/tasks/new" className="btn-primary">Create a task</Link>}
        />
      )}

      {!isLoading && !error && tasks.length > 0 && (
        <>
          {deleteError && <ErrorState message={deleteError} />}
          {tasks.map((task) => (
            <TaskRow
              key={task.id}
              task={task}
              onStatusChange={changeStatus}
              onDelete={setPendingDelete}
            />
          ))}
          <Pagination currentPage={page} numPages={numPages} onPageChange={setPage} />
        </>
      )}

      <ConfirmDialog
        open={!!pendingDelete}
        title={`Delete "${pendingDelete?.title}"?`}
        description="This can't be undone."
        confirmLabel="Delete"
        onCancel={() => setPendingDelete(null)}
        onConfirm={async () => {
          try {
            await removeTask(pendingDelete.id);
            setPendingDelete(null);
          } catch (err) {
            setDeleteError(extractErrorMessage(err));
            setPendingDelete(null);
          }
        }}
      />
    </div>
  );
}
