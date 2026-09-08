import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { FormField } from "../components/ui/FormField";
import { extractErrorMessage } from "../services/api";
import {
  validateConfirmPassword,
  validateEmail,
  validateName,
  validatePassword,
} from "../utils/validators";

export function RegisterPage() {
  const { register, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirmPassword: "" });
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const fieldErrors = {
      name: validateName(form.name),
      email: validateEmail(form.email),
      password: validatePassword(form.password),
      confirmPassword: validateConfirmPassword(form.password, form.confirmPassword),
    };
    setErrors(fieldErrors);
    if (Object.values(fieldErrors).some(Boolean)) return;

    setFormError("");
    setIsSubmitting(true);
    try {
      await register(form.name, form.email, form.password);
      await login(form.email, form.password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setFormError(extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <h1 style={{ fontSize: "1.3rem", marginBottom: "var(--space-5)" }}>Create your account</h1>
      <form onSubmit={handleSubmit} noValidate>
        <FormField label="Name" htmlFor="name" error={errors.name}>
          <input id="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </FormField>
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
            autoComplete="new-password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </FormField>
        <FormField label="Confirm password" htmlFor="confirmPassword" error={errors.confirmPassword}>
          <input
            id="confirmPassword"
            type="password"
            autoComplete="new-password"
            value={form.confirmPassword}
            onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
          />
        </FormField>
        {formError && <p className="field-error" role="alert" style={{ marginBottom: "var(--space-4)" }}>{formError}</p>}
        <button type="submit" className="btn-primary" disabled={isSubmitting} style={{ width: "100%" }}>
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>
      </form>
      <p style={{ marginTop: "var(--space-4)", fontSize: "0.9rem", color: "var(--color-ink-muted)" }}>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </>
  );
}
