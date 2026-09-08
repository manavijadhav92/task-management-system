/**
 * Centralized read/write for auth tokens, so the storage mechanism
 * (currently localStorage) is never referenced directly anywhere else in
 * the app - swapping storage strategies later means changing only this
 * file.
 */

const ACCESS_KEY = "tms_access_token";
const REFRESH_KEY = "tms_refresh_token";

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  setTokens: (access, refresh) => {
    localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  },
  setAccess: (access) => localStorage.setItem(ACCESS_KEY, access),
  clear: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};
