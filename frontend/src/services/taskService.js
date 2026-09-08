import { api } from "./api";

export const taskService = {
  list: (params) => api.get("/tasks/", { params }),
  stats: () => api.get("/tasks/stats/"),
  get: (id) => api.get(`/tasks/${id}/`),
  create: (payload) => api.post("/tasks/", payload),
  update: (id, payload) => api.put(`/tasks/${id}/`, payload),
  partialUpdate: (id, payload) => api.patch(`/tasks/${id}/`, payload),
  remove: (id) => api.delete(`/tasks/${id}/`),
  changeStatus: (id, status) => api.patch(`/tasks/${id}/status/`, { status }),
};
