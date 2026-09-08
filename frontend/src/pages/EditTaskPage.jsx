import { useNavigate, useParams } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { TaskForm } from "../components/tasks/TaskForm";
import { taskService } from "../services/taskService";
import { extractErrorMessage } from "../services/api";
import { Spinner } from "../components/ui/Spinner";
import { ErrorState } from "../components/ui/ErrorState";

export function EditTaskPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: task, isLoading, error, refetch } = useFetch(async () => {
    const { data } = await taskService.get(id);
    return data.data;
  }, [id]);

  const handleSubmit = async (values) => {
    try {
      await taskService.update(id, values);
      navigate(`/tasks/${id}`);
    } catch (err) {
      throw new Error(extractErrorMessage(err));
    }
  };

  if (isLoading) return <Spinner label="Loading task..." />;
  if (error) return <ErrorState message={extractErrorMessage(error)} onRetry={refetch} />;

  return (
    <div>
      <h1 style={{ fontSize: "1.4rem", marginBottom: "var(--space-5)" }}>Edit task</h1>
      <div className="card" style={{ padding: "var(--space-5)", maxWidth: 560 }}>
        <TaskForm initialValues={task} onSubmit={handleSubmit} submitLabel="Save changes" />
      </div>
    </div>
  );
}
