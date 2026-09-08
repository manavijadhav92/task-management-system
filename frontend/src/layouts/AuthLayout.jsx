import { Outlet } from "react-router-dom";
import "./auth-layout.css";

export function AuthLayout() {
  return (
    <div className="auth-shell">
      <div className="auth-card card">
        <div className="auth-brand">TaskFlow</div>
        <Outlet />
      </div>
    </div>
  );
}
