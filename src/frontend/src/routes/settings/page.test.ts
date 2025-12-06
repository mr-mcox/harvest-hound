import { render, screen, waitFor } from "@testing-library/svelte";
import { describe, it, expect, vi, beforeEach } from "vitest";
import SettingsPage from "./+page.svelte";

describe("Settings Page", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders all three sections after loading", async () => {
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes("household-profile")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              content: "Test household",
              updated_at: "2025-01-01T00:00:00Z",
            }),
        });
      }
      if (url.includes("pantry")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              content: "Test pantry",
              updated_at: "2025-01-01T00:00:00Z",
            }),
        });
      }
      if (url.includes("grocery-stores")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve([
              {
                id: 1,
                name: "Test Store",
                description: "Test",
                created_at: "2025-01-01T00:00:00Z",
              },
            ]),
        });
      }
      return Promise.reject(new Error("Unknown URL"));
    });
    vi.stubGlobal("fetch", mockFetch);

    render(SettingsPage);

    // Wait for loading to complete and sections to appear
    await waitFor(() => {
      expect(screen.getByText("Household Profile")).toBeInTheDocument();
    });

    expect(screen.getByText("Pantry")).toBeInTheDocument();
    expect(screen.getByText("Grocery Stores")).toBeInTheDocument();
    expect(screen.getByText("Test Store")).toBeInTheDocument();
  });

  it("back navigation link exists", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ content: "", updated_at: "" }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(SettingsPage);

    const backLink = screen.getByRole("link", { name: /back to home/i });
    expect(backLink).toHaveAttribute("href", "/");
  });
});
