import { render, screen, waitFor } from "@testing-library/svelte";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { goto } from "$app/navigation";
import ImportPage from "./+page.svelte";

describe("Inventory Import Page", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.mocked(goto).mockClear();
  });

  it("renders the import form with textarea and parse button", () => {
    render(ImportPage);

    expect(screen.getByText("Import Ingredients")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/paste your csa delivery/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /parse ingredients/i })
    ).toBeInTheDocument();
  });

  it("parses ingredients and displays pending items", async () => {
    const user = userEvent.setup();
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          ingredients: [
            {
              ingredient_name: "Tomatoes",
              quantity: 3,
              unit: "lb",
              priority: "High",
              portion_size: null,
            },
            {
              ingredient_name: "Kale",
              quantity: 1,
              unit: "bunch",
              priority: "Urgent",
              portion_size: null,
            },
          ],
          parsing_notes: null,
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(ImportPage);

    const textarea = screen.getByPlaceholderText(/paste your csa delivery/i);
    await user.type(textarea, "3 lbs tomatoes\n1 bunch kale");

    const parseButton = screen.getByRole("button", {
      name: /parse ingredients/i,
    });
    await user.click(parseButton);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });
    expect(screen.getByText("Kale")).toBeInTheDocument();

    // Verify API was called correctly
    expect(mockFetch).toHaveBeenCalledWith("/api/inventory/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        free_text: "3 lbs tomatoes\n1 bunch kale",
        configuration_instructions: null,
      }),
    });
  });

  it("allows deleting individual pending items", async () => {
    const user = userEvent.setup();
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          ingredients: [
            {
              ingredient_name: "Tomatoes",
              quantity: 3,
              unit: "lb",
              priority: "High",
              portion_size: null,
            },
            {
              ingredient_name: "Kale",
              quantity: 1,
              unit: "bunch",
              priority: "Urgent",
              portion_size: null,
            },
          ],
          parsing_notes: null,
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(ImportPage);

    // Parse first
    const textarea = screen.getByPlaceholderText(/paste your csa delivery/i);
    await user.type(textarea, "3 lbs tomatoes\n1 bunch kale");
    await user.click(screen.getByRole("button", { name: /parse ingredients/i }));

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Delete tomatoes
    const deleteButtons = screen.getAllByRole("button", { name: /delete/i });
    await user.click(deleteButtons[0]);

    // Tomatoes should be gone, kale should remain
    expect(screen.queryByText("Tomatoes")).not.toBeInTheDocument();
    expect(screen.getByText("Kale")).toBeInTheDocument();
  });

  it("appends new parsed items to existing pending items", async () => {
    const user = userEvent.setup();
    let callCount = 0;
    const mockFetch = vi.fn().mockImplementation(() => {
      callCount++;
      if (callCount === 1) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              ingredients: [
                {
                  ingredient_name: "Tomatoes",
                  quantity: 3,
                  unit: "lb",
                  priority: "High",
                  portion_size: null,
                },
              ],
              parsing_notes: null,
            }),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            ingredients: [
              {
                ingredient_name: "Carrots",
                quantity: 2,
                unit: "lb",
                priority: "Medium",
                portion_size: null,
              },
            ],
            parsing_notes: null,
          }),
      });
    });
    vi.stubGlobal("fetch", mockFetch);

    render(ImportPage);

    // First parse
    const textarea = screen.getByPlaceholderText(/paste your csa delivery/i);
    await user.type(textarea, "3 lbs tomatoes");
    await user.click(screen.getByRole("button", { name: /parse ingredients/i }));

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Second parse - should append
    await user.clear(textarea);
    await user.type(textarea, "2 lbs carrots");
    await user.click(screen.getByRole("button", { name: /parse ingredients/i }));

    await waitFor(() => {
      expect(screen.getByText("Carrots")).toBeInTheDocument();
    });

    // Both should be present
    expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    expect(screen.getByText("Carrots")).toBeInTheDocument();
  });

  it("approves pending items and clears the list", async () => {
    const user = userEvent.setup();
    let parseCallMade = false;
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes("/parse")) {
        parseCallMade = true;
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              ingredients: [
                {
                  ingredient_name: "Tomatoes",
                  quantity: 3,
                  unit: "lb",
                  priority: "High",
                  portion_size: null,
                },
              ],
              parsing_notes: null,
            }),
        });
      }
      if (url.includes("/bulk")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ saved_count: 1 }),
        });
      }
      return Promise.reject(new Error("Unknown URL"));
    });
    vi.stubGlobal("fetch", mockFetch);

    render(ImportPage);

    // Parse first
    const textarea = screen.getByPlaceholderText(/paste your csa delivery/i);
    await user.type(textarea, "3 lbs tomatoes");
    await user.click(screen.getByRole("button", { name: /parse ingredients/i }));

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Approve all
    const approveButton = screen.getByRole("button", { name: /approve all/i });
    await user.click(approveButton);

    // Verify bulk API was called
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith("/api/inventory/bulk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: [
            {
              ingredient_name: "Tomatoes",
              quantity: 3,
              unit: "lb",
              priority: "High",
              portion_size: null,
            },
          ],
        }),
      });
    });

    // Pending list should be cleared
    await waitFor(() => {
      expect(screen.queryByText("Tomatoes")).not.toBeInTheDocument();
    });
  });

  it("sends configuration instructions with parse request", async () => {
    const user = userEvent.setup();
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          ingredients: [
            {
              ingredient_name: "Ground Beef",
              quantity: 5,
              unit: "lb",
              priority: "Low",
              portion_size: "1 lb",
            },
          ],
          parsing_notes: null,
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(ImportPage);

    const textarea = screen.getByPlaceholderText(/paste your csa delivery/i);
    await user.type(textarea, "5 lbs ground beef");

    const configTextarea = screen.getByPlaceholderText(/configuration/i);
    await user.type(configTextarea, "All frozen in 1lb portions");

    await user.click(screen.getByRole("button", { name: /parse ingredients/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith("/api/inventory/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          free_text: "5 lbs ground beef",
          configuration_instructions: "All frozen in 1lb portions",
        }),
      });
    });
  });

  it("has navigation link back to inventory", () => {
    render(ImportPage);

    const backLink = screen.getByRole("link", { name: /back to inventory/i });
    expect(backLink).toHaveAttribute("href", "/inventory");
  });

  it("redirects to inventory list after successful approval", async () => {
    const user = userEvent.setup();
    const mockFetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes("/parse")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              ingredients: [
                {
                  ingredient_name: "Tomatoes",
                  quantity: 3,
                  unit: "lb",
                  priority: "High",
                  portion_size: null,
                },
              ],
              parsing_notes: null,
            }),
        });
      }
      if (url.includes("/bulk")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ saved_count: 1 }),
        });
      }
      return Promise.reject(new Error("Unknown URL"));
    });
    vi.stubGlobal("fetch", mockFetch);

    render(ImportPage);

    // Parse first
    const textarea = screen.getByPlaceholderText(/paste your csa delivery/i);
    await user.type(textarea, "3 lbs tomatoes");
    await user.click(screen.getByRole("button", { name: /parse ingredients/i }));

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Approve all
    const approveButton = screen.getByRole("button", { name: /approve all/i });
    await user.click(approveButton);

    // Verify redirect was called
    await waitFor(() => {
      expect(goto).toHaveBeenCalledWith("/inventory");
    });
  });
});
