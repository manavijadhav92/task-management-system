import { Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch";
import { taskService } from "../services/taskService";
import { extractErrorMessage } from "../services/api";
import { Spinner } from "../components/ui/Spinner";
import { ErrorState } from "../components/ui/ErrorState";
import "./dashboard.css";

const CARDS = [
  { key: "total", label: "Total tasks" },
  { key: "todo", label: "Pending" },
  { key: "in_progress", label: "In progress" },
  { key: "completed", label: "Completed" },
  { key: "high_priority_open", label: "High priority (open)" },
];

export function DashboardPage() {
  const { data, isLoading, error, refetch } = useFetch(async () => {
    const { data } = await taskService.stats();
    return data.data;
  }, []);

  if (isLoading) return <Spinner label="Loading dashboard..." />;
  if (error) return <ErrorState message={extractErrorMessage(error)} onRetry={refetch} />;

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "var(--space-5)" }}>
        <h1 style={{ fontSize: "1.4rem" }}>Dashboard</h1>
        <Link to="/tasks/new" className="btn-primary">New task</Link>
      </div>
      <div className="dashboard-grid">
        {CARDS.map((card) => (
          <div key={card.key} className="card dashboard-card">
            <span className="dashboard-card-value">{data[card.key]}</span>
            <span className="dashboard-card-label">{card.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
