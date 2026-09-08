import { Link } from "react-router-dom";
import { formatDate } from "../../utils/formatDate";
import { TASK_STATUSES } from "../../utils/constants";
import { PriorityBadge } from "./PriorityBadge";
import "./task-row.css";

export function TaskRow({ task, onStatusChange, onDelete }) {
  return (
    <div className="task-row card">
      <div className="task-row-main">
        <Link to={`/tasks/${task.id}`} className="task-row-title">
          {task.title}
        </Link>
        <div className="task-row-meta">
          <PriorityBadge priority={task.priority} />
          <span className="mono task-row-due">Due {formatDate(task.due_date)}</span>
        </div>
      </div>
      <div className="task-row-actions">
        <select
          aria-label={`Change status for ${task.title}`}
          value={task.status}
          onChange={(e) => onStatusChange(task.id, e.target.value)}
        >
          {TASK_STATUSES.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
        <Link to={`/tasks/${task.id}/edit`} className="btn-text">Edit</Link>
        <button type="button" className="btn-text" onClick={() => onDelete(task)}>Delete</button>
      </div>
    </div>
  );
}
