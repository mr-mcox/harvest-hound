import { render, screen, waitFor } from "@testing-library/svelte";
import { describe, it, expect, vi, beforeEach } from "vitest";
import InventoryPage from "./+page.svelte";

describe("Inventory List Page", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the inventory list heading and import button", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    expect(screen.getByText("Inventory")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /import ingredients/i })).toHaveAttribute(
      "href",
      "/inventory/import"
    );
  });

  it("fetches and displays inventory items", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
          {
            id: 2,
            ingredient_name: "Kale",
            quantity: 1,
            unit: "bunch",
            priority: "Urgent",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });
    expect(screen.getByText("Kale")).toBeInTheDocument();

    // Verify API was called
    expect(mockFetch).toHaveBeenCalledWith("/api/inventory");
  });

  it("displays items sorted by priority (Urgent > High > Medium > Low)", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Carrots",
            quantity: 2,
            unit: "lb",
            priority: "Low",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
          {
            id: 2,
            ingredient_name: "Spinach",
            quantity: 1,
            unit: "bunch",
            priority: "Urgent",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
          {
            id: 3,
            ingredient_name: "Tomatoes",
            quantity: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
          {
            id: 4,
            ingredient_name: "Onions",
            quantity: 2,
            unit: "lb",
            priority: "Medium",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Spinach")).toBeInTheDocument();
    });

    // Get all table rows (excluding header) and verify order
    const rows = screen.getAllByRole("row");
    expect(rows[1]).toHaveTextContent("Spinach"); // Urgent first (index 1 skips header)
    expect(rows[2]).toHaveTextContent("Tomatoes"); // High second
    expect(rows[3]).toHaveTextContent("Onions"); // Medium third
    expect(rows[4]).toHaveTextContent("Carrots"); // Low last
  });

  it("displays quantity, unit, and priority for each item", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });
    expect(screen.getByText(/3/)).toBeInTheDocument();
    expect(screen.getByText(/lb/)).toBeInTheDocument();
    expect(screen.getByText("High")).toBeInTheDocument();
  });

  it("displays portion size when present", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Ground Beef",
            quantity: 5,
            unit: "lb",
            priority: "Medium",
            portion_size: "1 lb",
            added_at: "2025-01-01T00:00:00Z",
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Ground Beef")).toBeInTheDocument();
    });
    expect(screen.getByText(/1 lb portions/i)).toBeInTheDocument();
  });

  it("shows empty state when no inventory items", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText(/no items in inventory/i)).toBeInTheDocument();
    });
  });

  it("shows error state when fetch fails", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
    });
  });

  it("hides items with quantity = 0 from display", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
          {
            id: 2,
            ingredient_name: "Consumed Item",
            quantity: 0,
            unit: "lb",
            priority: "Medium",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
          {
            id: 3,
            ingredient_name: "Kale",
            quantity: 1,
            unit: "bunch",
            priority: "Urgent",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Items with quantity > 0 should be visible
    expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    expect(screen.getByText("Kale")).toBeInTheDocument();

    // Item with quantity = 0 should NOT be visible
    expect(screen.queryByText("Consumed Item")).not.toBeInTheDocument();
  });

  it("deletes item when delete button is clicked (optimistic update)", async () => {
    const mockFetch = vi.fn();
    // First call: GET inventory
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
          {
            id: 2,
            ingredient_name: "Kale",
            quantity: 1,
            unit: "bunch",
            priority: "Urgent",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
        ]),
    });
    // Second call: DELETE item
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ deleted: true, id: 1 }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });
    expect(screen.getByText("Kale")).toBeInTheDocument();

    // Click delete button for Tomatoes
    const deleteButton = screen.getByLabelText("Delete Tomatoes");
    deleteButton.click();

    // Item should be removed immediately (optimistic update)
    await waitFor(() => {
      expect(screen.queryByText("Tomatoes")).not.toBeInTheDocument();
    });
    expect(screen.getByText("Kale")).toBeInTheDocument();

    // Verify DELETE API was called
    expect(mockFetch).toHaveBeenCalledWith("/api/inventory/1", {
      method: "DELETE",
    });
  });

  it("restores item when delete fails", async () => {
    const mockFetch = vi.fn();
    // First call: GET inventory
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
          },
        ]),
    });
    // Second call: DELETE fails
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Click delete button
    const deleteButton = screen.getByLabelText("Delete Tomatoes");
    deleteButton.click();

    // Item should be restored after failed delete
    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Error message should be shown
    expect(screen.getByText(/failed to delete/i)).toBeInTheDocument();
  });
});
