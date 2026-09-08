/**
 * Frontend form validation. These mirror (but do not replace) backend
 * validation - the backend remains the source of truth, this just gives
 * the user faster, friendlier feedback before a round trip.
 */

export function validateEmail(value) {
  if (!value) return "Email is required.";
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value)) return "Enter a valid email address.";
  return "";
}

export function validatePassword(value) {
  if (!value) return "Password is required.";
  if (value.length < 8) return "Password must be at least 8 characters.";
  if (!/[a-zA-Z]/.test(value) || !/[0-9]/.test(value)) {
    return "Password must contain at least one letter and one number.";
  }
  return "";
}

export function validateConfirmPassword(password, confirm) {
  if (!confirm) return "Please confirm your password.";
  if (password !== confirm) return "Passwords do not match.";
  return "";
}

export function validateName(value) {
  if (!value || !value.trim()) return "Name is required.";
  return "";
}

export function validateTaskTitle(value) {
  if (!value || !value.trim()) return "Title is required.";
  if (value.trim().length > 200) return "Title must be under 200 characters.";
  return "";
}
