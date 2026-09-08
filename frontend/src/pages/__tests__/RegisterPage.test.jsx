import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { RegisterPage } from "../RegisterPage";
import { useAuth } from "../../hooks/useAuth";

vi.mock("../../hooks/useAuth");

const navigateMock = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => navigateMock };
});

describe("RegisterPage", () => {
  const registerMock = vi.fn();
  const loginMock = vi.fn();

  beforeEach(() => {
    navigateMock.mockClear();
    registerMock.mockReset();
    loginMock.mockReset();
    useAuth.mockReturnValue({ register: registerMock, login: loginMock });
  });

  it("validates all fields before submitting", async () => {
    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    await userEvent.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByText(/name is required/i)).toBeInTheDocument();
    expect(registerMock).not.toHaveBeenCalled();
  });

  it("rejects mismatched passwords", async () => {
    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    await userEvent.type(screen.getByLabelText(/^name$/i), "Manavi");
    await userEvent.type(screen.getByLabelText(/^email$/i), "manavi@example.com");
    await userEvent.type(screen.getByLabelText(/^password$/i), "Passw0rd1");
    await userEvent.type(screen.getByLabelText(/confirm password/i), "Different1");
    await userEvent.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument();
    expect(registerMock).not.toHaveBeenCalled();
  });

  it("registers, logs in, and navigates to the dashboard on success", async () => {
    registerMock.mockResolvedValue({ id: "1", email: "manavi@example.com" });
    loginMock.mockResolvedValue({ name: "Manavi" });

    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    await userEvent.type(screen.getByLabelText(/^name$/i), "Manavi");
    await userEvent.type(screen.getByLabelText(/^email$/i), "manavi@example.com");
    await userEvent.type(screen.getByLabelText(/^password$/i), "Passw0rd1");
    await userEvent.type(screen.getByLabelText(/confirm password/i), "Passw0rd1");
    await userEvent.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => expect(registerMock).toHaveBeenCalledWith("Manavi", "manavi@example.com", "Passw0rd1"));
    await waitFor(() => expect(loginMock).toHaveBeenCalledWith("manavi@example.com", "Passw0rd1"));
    expect(navigateMock).toHaveBeenCalledWith("/dashboard", { replace: true });
  });
});
