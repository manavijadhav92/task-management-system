import { useCallback, useEffect, useState } from "react";
import { taskService } from "../services/taskService";
import { extractErrorMessage } from "../services/api";
import { useDebounce } from "./useDebounce";

const DEFAULT_FILTERS = { search: "", status: "", priority: "", ordering: "-created_at" };

/**
 * Owns the task-list state: current filters, current page, and the fetched
 * page of results. Re-fetches whenever filters or page change (search is
 * debounced internally so typing doesn't fire a request per keystroke).
 * Also exposes changeStatus/removeTask so the list can update itself
 * without the caller needing to know about refetching.
 */
export function useTasks() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [page, setPage] = useState(1);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const debouncedSearch = useDebounce(filters.search, 400);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      const { data } = await taskService.list({
        page,
        status: filters.status || undefined,
        priority: filters.priority || undefined,
        search: debouncedSearch || undefined,
        ordering: filters.ordering,
      });
      setResult(data.data);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filters.status, filters.priority, filters.ordering, debouncedSearch]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  useEffect(() => {
    setPage(1);
  }, [filters.status, filters.priority, filters.ordering, debouncedSearch]);

  const changeStatus = useCallback(async (taskId, status) => {
    const { data } = await taskService.changeStatus(taskId, status);
    setResult((prev) =>
      prev
        ? { ...prev, results: prev.results.map((t) => (t.id === taskId ? data.data : t)) }
        : prev
    );
  }, []);

  const removeTask = useCallback(async (taskId) => {
    await taskService.remove(taskId);
    fetchTasks();
  }, [fetchTasks]);

  return {
    filters,
    setFilters,
    page,
    setPage,
    tasks: result?.results || [],
    count: result?.count || 0,
    numPages: result?.num_pages || 1,
    isLoading,
    error,
    refetch: fetchTasks,
    changeStatus,
    removeTask,
  };
}
