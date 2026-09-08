import { useNavigate } from "react-router-dom";
import { TaskForm } from "../components/tasks/TaskForm";
import { taskService } from "../services/taskService";
import { extractErrorMessage } from "../services/api";

export function CreateTaskPage() {
  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    try {
      const { data } = await taskService.create(values);
      navigate(`/tasks/${data.data.id}`);
    } catch (err) {
      throw new Error(extractErrorMessage(err));
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: "1.4rem", marginBottom: "var(--space-5)" }}>New task</h1>
      <div className="card" style={{ padding: "var(--space-5)", maxWidth: 560 }}>
        <TaskForm onSubmit={handleSubmit} submitLabel="Create task" />
      </div>
    </div>
  );
}
