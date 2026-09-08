import { TASK_PRIORITIES, TASK_STATUSES } from "../../utils/constants";
import "./task-filters.css";

export function TaskFilters({ filters, onChange }) {
  const update = (patch) => onChange({ ...filters, ...patch });

  return (
    <div className="task-filters">
      <input
        type="search"
        placeholder="Search tasks..."
        aria-label="Search tasks"
        value={filters.search}
        onChange={(e) => update({ search: e.target.value })}
      />
      <select
        aria-label="Filter by status"
        value={filters.status}
        onChange={(e) => update({ status: e.target.value })}
      >
        <option value="">All statuses</option>
        {TASK_STATUSES.map((s) => (
          <option key={s.value} value={s.value}>{s.label}</option>
        ))}
      </select>
      <select
        aria-label="Filter by priority"
        value={filters.priority}
        onChange={(e) => update({ priority: e.target.value })}
      >
        <option value="">All priorities</option>
        {TASK_PRIORITIES.map((p) => (
          <option key={p.value} value={p.value}>{p.label}</option>
        ))}
      </select>
      <select
        aria-label="Sort tasks"
        value={filters.ordering}
        onChange={(e) => update({ ordering: e.target.value })}
      >
        <option value="-created_at">Newest first</option>
        <option value="created_at">Oldest first</option>
        <option value="due_date">Due date</option>
        <option value="title">Title (A-Z)</option>
        <option value="priority">Priority</option>
      </select>
    </div>
  );
}
