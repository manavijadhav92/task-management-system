import { priorityLabel } from "../../utils/constants";
import "./badges.css";

const DOT_VAR = {
  LOW: "--priority-low",
  MEDIUM: "--priority-medium",
  HIGH: "--priority-high",
};

export function PriorityBadge({ priority }) {
  return (
    <span className="badge">
      <span className="badge-dot" style={{ background: `var(${DOT_VAR[priority]})` }} />
      {priorityLabel(priority)}
    </span>
  );
}
