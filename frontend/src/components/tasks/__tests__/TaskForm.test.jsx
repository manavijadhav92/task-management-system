import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { TaskForm } from "../TaskForm";

describe("TaskForm", () => {
  it("shows a validation error for a blank title and does not submit", async () => {
    const onSubmit = vi.fn();
    render(<TaskForm onSubmit={onSubmit} />);

    await userEvent.click(screen.getByRole("button", { name: /save task/i }));

    expect(await screen.findByText(/title is required/i)).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits the entered values for a new task", async () => {
    const onSubmit = vi.fn().mockResolvedValue();
    render(<TaskForm onSubmit={onSubmit} submitLabel="Create task" />);

    await userEvent.type(screen.getByLabelText(/title/i), "Write report");
    await userEvent.type(screen.getByLabelText(/description/i), "Q3 report");
    await userEvent.selectOptions(screen.getByLabelText(/priority/i), "HIGH");
    await userEvent.click(screen.getByRole("button", { name: /create task/i }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    const submitted = onSubmit.mock.calls[0][0];
    expect(submitted.title).toBe("Write report");
    expect(submitted.description).toBe("Q3 report");
    expect(submitted.priority).toBe("HIGH");
  });

  it("pre-fills fields from initialValues when editing", () => {
    render(
      <TaskForm
        initialValues={{ title: "Existing task", description: "", status: "IN_PROGRESS", priority: "LOW" }}
        onSubmit={vi.fn()}
      />
    );
    expect(screen.getByLabelText(/title/i)).toHaveValue("Existing task");
    expect(screen.getByLabelText(/priority/i)).toHaveValue("LOW");
  });

  it("surfaces a server error message without crashing", async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error("Something went wrong."));
    render(<TaskForm onSubmit={onSubmit} />);

    await userEvent.type(screen.getByLabelText(/title/i), "A task");
    await userEvent.click(screen.getByRole("button", { name: /save task/i }));

    expect(await screen.findByText(/something went wrong/i)).toBeInTheDocument();
  });
});
