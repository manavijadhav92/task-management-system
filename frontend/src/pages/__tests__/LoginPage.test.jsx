import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { LoginPage } from "../LoginPage";
import { useAuth } from "../../hooks/useAuth";

vi.mock("../../hooks/useAuth");

const navigateMock = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => navigateMock,
    useLocation: () => ({ state: null }),
  };
});

describe("LoginPage", () => {
  const loginMock = vi.fn();

  beforeEach(() => {
    navigateMock.mockClear();
    loginMock.mockReset();
    useAuth.mockReturnValue({ login: loginMock });
  });

  it("shows validation errors and does not call login for empty fields", async () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
    expect(loginMock).not.toHaveBeenCalled();
  });

  it("logs in and navigates to the dashboard on success", async () => {
    loginMock.mockResolvedValue({ name: "Manavi" });
    render(<MemoryRouter><LoginPage /></MemoryRouter>);

    await userEvent.type(screen.getByLabelText(/email/i), "manavi@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "Passw0rd1");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => expect(loginMock).toHaveBeenCalledWith("manavi@example.com", "Passw0rd1"));
    expect(navigateMock).toHaveBeenCalledWith("/dashboard", { replace: true });
  });

  it("shows a server error message on failed login", async () => {
    loginMock.mockRejectedValue({ response: { data: { message: "Invalid email or password.", errors: {} } } });
    render(<MemoryRouter><LoginPage /></MemoryRouter>);

    await userEvent.type(screen.getByLabelText(/email/i), "manavi@example.com");
    await userEvent.type(screen.getByLabelText(/password/i), "WrongPass1");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    expect(await screen.findByText(/invalid email or password/i)).toBeInTheDocument();
  });
});
