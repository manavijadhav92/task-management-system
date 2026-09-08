export const TASK_STATUSES = [
  { value: "TODO", label: "To do" },
  { value: "IN_PROGRESS", label: "In progress" },
  { value: "COMPLETED", label: "Completed" },
];

export const TASK_PRIORITIES = [
  { value: "LOW", label: "Low" },
  { value: "MEDIUM", label: "Medium" },
  { value: "HIGH", label: "High" },
];

export const statusLabel = (value) =>
  TASK_STATUSES.find((s) => s.value === value)?.label || value;

export const priorityLabel = (value) =>
  TASK_PRIORITIES.find((p) => p.value === value)?.label || value;
