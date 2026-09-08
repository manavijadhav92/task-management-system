import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { TaskListPage } from "../TaskListPage";
import { taskService } from "../../services/taskService";

vi.mock("../../services/taskService");

function makeTask(overrides = {}) {
  return {
    id: "1",
    title: "Write report",
    description: "",
    status: "TODO",
    priority: "HIGH",
    due_date: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

function makePage(tasks) {
  return { results: tasks, count: tasks.length, num_pages: 1, current_page: 1 };
}

describe("TaskListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows a loading state, then the fetched tasks", async () => {
    taskService.list.mockResolvedValue({ data: { data: makePage([makeTask()]) } });
    render(<MemoryRouter><TaskListPage /></MemoryRouter>);

    expect(screen.getByText(/loading tasks/i)).toBeInTheDocument();
    expect(await screen.findByText("Write report")).toBeInTheDocument();
  });

  it("shows an empty state when there are no tasks", async () => {
    taskService.list.mockResolvedValue({ data: { data: makePage([]) } });
    render(<MemoryRouter><TaskListPage /></MemoryRouter>);

    expect(await screen.findByText(/no tasks found/i)).toBeInTheDocument();
  });

  it("shows an error state with a retry option when the fetch fails", async () => {
    taskService.list.mockRejectedValue({ response: { data: { message: "Server error", errors: {} } } });
    render(<MemoryRouter><TaskListPage /></MemoryRouter>);

    expect(await screen.findByText(/server error/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument();
  });

  it("asks for confirmation before deleting a task, then deletes it", async () => {
    taskService.list.mockResolvedValue({ data: { data: makePage([makeTask()]) } });
    taskService.remove.mockResolvedValue({});

    render(<MemoryRouter><TaskListPage /></MemoryRouter>);
    await screen.findByText("Write report");

    await userEvent.click(screen.getByRole("button", { name: /delete/i }));

    const dialog = await screen.findByRole("alertdialog");
    expect(within(dialog).getByText(/write report/i)).toBeInTheDocument();

    taskService.list.mockResolvedValue({ data: { data: makePage([]) } });
    await userEvent.click(within(dialog).getByRole("button", { name: /^delete$/i }));

    await waitFor(() => expect(taskService.remove).toHaveBeenCalledWith("1"));
  });

  it("changes a task's status from the row selector", async () => {
    taskService.list.mockResolvedValue({ data: { data: makePage([makeTask()]) } });
    taskService.changeStatus.mockResolvedValue({ data: { data: makeTask({ status: "IN_PROGRESS" }) } });

    render(<MemoryRouter><TaskListPage /></MemoryRouter>);
    await screen.findByText("Write report");

    await userEvent.selectOptions(screen.getByLabelText(/change status for write report/i), "IN_PROGRESS");

    await waitFor(() => expect(taskService.changeStatus).toHaveBeenCalledWith("1", "IN_PROGRESS"));
  });
});
