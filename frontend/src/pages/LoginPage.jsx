import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { FormField } from "../components/ui/FormField";
import { extractErrorMessage } from "../services/api";
import { validateEmail } from "../utils/validators";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const fieldErrors = {
      email: validateEmail(form.email),
      password: form.password ? "" : "Password is required.",
    };
    setErrors(fieldErrors);
    if (Object.values(fieldErrors).some(Boolean)) return;

    setFormError("");
    setIsSubmitting(true);
    try {
      await login(form.email, form.password);
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
    } catch (err) {
      setFormError(extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <h1 style={{ fontSize: "1.3rem", marginBottom: "var(--space-5)" }}>Log in</h1>
      <form onSubmit={handleSubmit} noValidate>
        <FormField label="Email" htmlFor="email" error={errors.email}>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </FormField>
        <FormField label="Password" htmlFor="password" error={errors.password}>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </FormField>
        {formError && <p className="field-error" role="alert" style={{ marginBottom: "var(--space-4)" }}>{formError}</p>}
        <button type="submit" className="btn-primary" disabled={isSubmitting} style={{ width: "100%" }}>
          {isSubmitting ? "Logging in..." : "Log in"}
        </button>
      </form>
      <p style={{ marginTop: "var(--space-4)", fontSize: "0.9rem", color: "var(--color-ink-muted)" }}>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
    </>
  );
}
