import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import App from "../src/App";

describe("App (Phase 1 scaffold)", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          status: "ok",
          service: "Business Workflow Automation Platform",
          environment: "test",
        }),
      })
    );
  });

  it("renders the page title", () => {
    render(<App />);
    expect(screen.getByText("Business Workflow Automation Platform")).toBeInTheDocument();
  });

  it("displays backend health once the fetch resolves", async () => {
    render(<App />);
    expect(await screen.findByText(/Status: ok/)).toBeInTheDocument();
  });
});
