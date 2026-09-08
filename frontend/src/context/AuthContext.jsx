import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { setOnAuthFailure } from "../services/api";
import { authService } from "../services/authService";
import { tokenStorage } from "../services/tokenStorage";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const clearSession = useCallback(() => {
    tokenStorage.clear();
    setUser(null);
  }, []);

  useEffect(() => {
    setOnAuthFailure(clearSession);
  }, [clearSession]);

  useEffect(() => {
    async function restoreSession() {
      if (!tokenStorage.getAccess()) {
        setIsLoading(false);
        return;
      }
      try {
        const { data } = await authService.me();
        setUser(data.data);
      } catch {
        clearSession();
      } finally {
        setIsLoading(false);
      }
    }
    restoreSession();
  }, [clearSession]);

  const login = useCallback(async (email, password) => {
    const { data } = await authService.login({ email, password });
    tokenStorage.setTokens(data.data.access, data.data.refresh);
    setUser(data.data.user);
    return data.data.user;
  }, []);

  const register = useCallback(async (name, email, password) => {
    const { data } = await authService.register({ name, email, password });
    return data.data;
  }, []);

  const logout = useCallback(async () => {
    const refresh = tokenStorage.getRefresh();
    try {
      if (refresh) await authService.logout(refresh);
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const value = useMemo(
    () => ({ user, isLoading, isAuthenticated: !!user, login, register, logout }),
    [user, isLoading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
