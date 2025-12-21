import { render, screen, waitFor, fireEvent } from "@testing-library/svelte";
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
            available: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
          {
            id: 2,
            ingredient_name: "Kale",
            quantity: 1,
            available: 1,
            unit: "bunch",
            priority: "Urgent",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });
    expect(screen.getByText("Kale")).toBeInTheDocument();

    // Verify API was called with claims endpoint
    expect(mockFetch).toHaveBeenCalledWith("/api/inventory/with-claims");
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
            available: 2,
            unit: "lb",
            priority: "Low",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
          {
            id: 2,
            ingredient_name: "Spinach",
            quantity: 1,
            available: 1,
            unit: "bunch",
            priority: "Urgent",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
          {
            id: 3,
            ingredient_name: "Tomatoes",
            quantity: 3,
            available: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
          {
            id: 4,
            ingredient_name: "Onions",
            quantity: 2,
            available: 2,
            unit: "lb",
            priority: "Medium",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
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
            available: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });
    expect(screen.getByText("3 lb")).toBeInTheDocument();
    expect(screen.getByText("High")).toBeInTheDocument();
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
            available: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
          {
            id: 2,
            ingredient_name: "Consumed Item",
            quantity: 0,
            available: 0,
            unit: "lb",
            priority: "Medium",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
          {
            id: 3,
            ingredient_name: "Kale",
            quantity: 1,
            available: 1,
            unit: "bunch",
            priority: "Urgent",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
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

  it("shows available quantity when partially claimed", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            available: 1,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [
              {
                recipe_id: "abc",
                recipe_name: "Tomato Soup",
                quantity: 2,
                unit: "lb",
              },
            ],
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Should show available quantity
    expect(screen.getByText("3 lb (1 avail)")).toBeInTheDocument();
  });

  it("shows fully claimed indicator when available = 0", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            available: 0,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [
              {
                recipe_id: "abc",
                recipe_name: "Tomato Soup",
                quantity: 3,
                unit: "lb",
              },
            ],
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Should show 0 available
    expect(screen.getByText("3 lb (0 avail)")).toBeInTheDocument();
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
            available: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
          {
            id: 2,
            ingredient_name: "Kale",
            quantity: 1,
            available: 1,
            unit: "bunch",
            priority: "Urgent",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
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
            available: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
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

  it("shows input when quantity is clicked for editing", async () => {
    const mockFetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            available: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Click on quantity to edit (button shows "3 lb" for unclaimed items)
    const quantityButton = screen.getByRole("button", { name: "3 lb" });
    quantityButton.click();

    // Input should appear with current quantity
    const input = await waitFor(() => screen.getByRole("spinbutton"));
    expect(input).toHaveValue(3);
  });

  it("rejects quantity <= 0 and cancels editing", async () => {
    const mockFetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            available: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Click on quantity to edit
    const quantityButton = screen.getByRole("button", { name: "3 lb" });
    quantityButton.click();

    const input = await waitFor(() => screen.getByRole("spinbutton"));
    await fireEvent.input(input, { target: { value: "0" } });
    await fireEvent.blur(input);

    // Quantity should remain 3 (rejected)
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "3 lb" })).toBeInTheDocument();
    });

    // PATCH should not have been called
    expect(mockFetch).toHaveBeenCalledTimes(1); // Only GET
  });

  it("shows dropdown when priority is clicked for editing", async () => {
    const mockFetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            available: 3,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [],
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Click on priority to edit
    const priorityButton = screen.getByRole("button", { name: "High" });
    priorityButton.click();

    // Wait for priority dropdown to appear (there are 2 comboboxes: filter and priority)
    await waitFor(() => {
      expect(screen.getAllByRole("combobox")).toHaveLength(2);
    });

    // The priority dropdown is the one without the claim-filter id
    const dropdowns = screen.getAllByRole("combobox");
    const priorityDropdown = dropdowns[1]; // Second combobox is the priority one
    expect(priorityDropdown).toHaveValue("High");

    // Verify all priority options are present in the priority dropdown
    const options = priorityDropdown.querySelectorAll("option");
    expect(options).toHaveLength(4);
    expect(options[0]).toHaveTextContent("Low");
    expect(options[1]).toHaveTextContent("Medium");
    expect(options[2]).toHaveTextContent("High");
    expect(options[3]).toHaveTextContent("Urgent");
  });

  it("shows claim indicator for items with claims", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve([
          {
            id: 1,
            ingredient_name: "Tomatoes",
            quantity: 3,
            available: 1,
            unit: "lb",
            priority: "High",
            portion_size: null,
            added_at: "2025-01-01T00:00:00Z",
            claims: [
              {
                recipe_id: "abc",
                recipe_name: "Tomato Soup",
                quantity: 2,
                unit: "lb",
              },
            ],
          },
        ]),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(InventoryPage);

    await waitFor(() => {
      expect(screen.getByText("Tomatoes")).toBeInTheDocument();
    });

    // Should show claim indicator (link emoji)
    expect(screen.getByLabelText(/view 1 claiming recipe/i)).toBeInTheDocument();
  });
});
