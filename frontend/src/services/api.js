/**
 * Centralized Axios instance.
 *
 * - Base URL comes from VITE_API_URL (never hardcoded).
 * - Every request automatically gets the access token attached.
 * - A 401 response triggers a single attempt to refresh the access token
 *   using the refresh token, then retries the original request. If the
 *   refresh itself fails, the user is logged out and sent to /login.
 * - Requests are queued while a refresh is already in flight, so a burst
 *   of parallel requests doesn't trigger multiple refresh calls.
 */

import axios from "axios";
import { tokenStorage } from "./tokenStorage";

const baseURL = import.meta.env.VITE_API_URL;

export const api = axios.create({ baseURL });

api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let pendingQueue = [];

function resolveQueue(error, token) {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  pendingQueue = [];
}

// Set by AuthContext so the interceptor can trigger a full logout when a
// refresh attempt fails, without importing React state into this module.
let onAuthFailure = () => {};
export function setOnAuthFailure(handler) {
  onAuthFailure = handler;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const isAuthEndpoint = originalRequest?.url?.includes("/auth/login") ||
      originalRequest?.url?.includes("/auth/register") ||
      originalRequest?.url?.includes("/auth/refresh");

    if (error.response?.status !== 401 || isAuthEndpoint || originalRequest._retry) {
      return Promise.reject(error);
    }

    const refreshToken = tokenStorage.getRefresh();
    if (!refreshToken) {
      onAuthFailure();
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({ resolve, reject });
      }).then((newToken) => {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        originalRequest._retry = true;
        return api(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const { data } = await axios.post(`${baseURL}/auth/refresh/`, {
        refresh: refreshToken,
      });
      const newAccess = data.data.access;
      tokenStorage.setAccess(newAccess);
      resolveQueue(null, newAccess);
      originalRequest.headers.Authorization = `Bearer ${newAccess}`;
      return api(originalRequest);
    } catch (refreshError) {
      resolveQueue(refreshError, null);
      onAuthFailure();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

/** Pulls a user-facing message out of the project's standard error shape. */
export function extractErrorMessage(error) {
  const body = error?.response?.data;
  if (!body) return "Network error. Please check your connection and try again.";
  if (body.errors && typeof body.errors === "object") {
    const firstField = Object.values(body.errors)[0];
    if (Array.isArray(firstField) && firstField.length) return firstField[0];
    if (typeof firstField === "string") return firstField;
  }
  return body.message || "Something went wrong.";
}
