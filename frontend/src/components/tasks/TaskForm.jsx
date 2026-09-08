import { useState } from "react";
import { FormField } from "../ui/FormField";
import { TASK_PRIORITIES, TASK_STATUSES } from "../../utils/constants";
import { validateTaskTitle } from "../../utils/validators";

export function TaskForm({ initialValues, onSubmit, submitLabel = "Save task" }) {
  const [values, setValues] = useState({
    title: initialValues?.title || "",
    description: initialValues?.description || "",
    status: initialValues?.status || "TODO",
    priority: initialValues?.priority || "MEDIUM",
    due_date: initialValues?.due_date ? initialValues.due_date.slice(0, 10) : "",
    assigned_to: initialValues?.assigned_to || "",
  });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const update = (patch) => setValues((prev) => ({ ...prev, ...patch }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const fieldErrors = { title: validateTaskTitle(values.title) };
    setErrors(fieldErrors);
    if (Object.values(fieldErrors).some(Boolean)) return;

    setFormError("");
    setIsSubmitting(true);
    try {
      await onSubmit({ ...values, due_date: values.due_date || null });
    } catch (err) {
      setFormError(err.message || "Something went wrong.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <FormField label="Title" htmlFor="title" error={errors.title}>
        <input id="title" value={values.title} onChange={(e) => update({ title: e.target.value })} />
      </FormField>

      <FormField label="Description" htmlFor="description">
        <textarea
          id="description"
          value={values.description}
          onChange={(e) => update({ description: e.target.value })}
        />
      </FormField>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-4)" }}>
        <FormField label="Status" htmlFor="status">
          <select id="status" value={values.status} onChange={(e) => update({ status: e.target.value })}>
            {TASK_STATUSES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </FormField>

        <FormField label="Priority" htmlFor="priority">
          <select id="priority" value={values.priority} onChange={(e) => update({ priority: e.target.value })}>
            {TASK_PRIORITIES.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
        </FormField>
      </div>

      <FormField label="Due date" htmlFor="due_date">
        <input
          id="due_date"
          type="date"
          value={values.due_date}
          onChange={(e) => update({ due_date: e.target.value })}
        />
      </FormField>

      <FormField label="Assign to (user ID, optional)" htmlFor="assigned_to">
        <input
          id="assigned_to"
          value={values.assigned_to}
          onChange={(e) => update({ assigned_to: e.target.value })}
        />
      </FormField>

      {formError && <p className="field-error" role="alert" style={{ marginBottom: "var(--space-4)" }}>{formError}</p>}

      <button type="submit" className="btn-primary" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}
