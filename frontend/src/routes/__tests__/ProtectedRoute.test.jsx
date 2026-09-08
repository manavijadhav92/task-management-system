import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { ProtectedRoute } from "../ProtectedRoute";
import { useAuth } from "../../hooks/useAuth";

vi.mock("../../hooks/useAuth");

function renderWithRoute(initialPath = "/tasks") {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/tasks" element={<div>Tasks page</div>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  it("shows a loading state while the session is being checked", () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isLoading: true });
    renderWithRoute();
    expect(screen.getByText(/checking your session/i)).toBeInTheDocument();
  });

  it("redirects unauthenticated users to /login", () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isLoading: false });
    renderWithRoute();
    expect(screen.getByText(/login page/i)).toBeInTheDocument();
  });

  it("renders the protected content for authenticated users", () => {
    useAuth.mockReturnValue({ isAuthenticated: true, isLoading: false });
    renderWithRoute();
    expect(screen.getByText(/tasks page/i)).toBeInTheDocument();
  });
});
