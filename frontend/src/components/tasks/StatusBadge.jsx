import { statusLabel } from "../../utils/constants";
import "./badges.css";

const DOT_VAR = {
  TODO: "--status-todo",
  IN_PROGRESS: "--status-in-progress",
  COMPLETED: "--status-completed",
};

export function StatusBadge({ status }) {
  return (
    <span className="badge">
      <span className="badge-dot" style={{ background: `var(${DOT_VAR[status]})` }} />
      {statusLabel(status)}
    </span>
  );
}
