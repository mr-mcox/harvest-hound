import { render, screen, fireEvent, waitFor } from "@testing-library/svelte";
import { describe, it, expect, vi, beforeEach } from "vitest";
import ConfigTextArea from "./ConfigTextArea.svelte";

describe("ConfigTextArea", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders with initial content", () => {
    render(ConfigTextArea, {
      props: {
        label: "Household Profile",
        apiEndpoint: "/api/config/household-profile",
        initialContent: "Test content here",
      },
    });

    const textarea = screen.getByRole("textbox");
    expect(textarea).toHaveValue("Test content here");
  });

  it("save button calls API and shows success feedback", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          content: "Updated content",
          updated_at: "2025-01-01T00:00:00Z",
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(ConfigTextArea, {
      props: {
        label: "Household Profile",
        apiEndpoint: "/api/config/household-profile",
        initialContent: "Initial content",
      },
    });

    const textarea = screen.getByRole("textbox");
    await fireEvent.input(textarea, { target: { value: "Updated content" } });

    const saveButton = screen.getByRole("button", { name: /save/i });
    await fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith("/api/config/household-profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: "Updated content" }),
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/saved/i)).toBeInTheDocument();
    });
  });
});
