import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../src/context/AuthContext";
import App from "../src/App";

function renderApp(initialPath = "/") {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("App routing", () => {
  it("redirects unauthenticated users to /login", () => {
    renderApp("/dashboard");
    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
  });

  it("renders the login page at /login", () => {
    renderApp("/login");
    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText("Business Workflow Automation Platform")).toBeInTheDocument();
  });

  it("renders the register link on the login page", () => {
    renderApp("/login");
    expect(screen.getByRole("link", { name: /register/i })).toBeInTheDocument();
  });
});
