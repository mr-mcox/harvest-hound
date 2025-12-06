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

    // Get all list items and verify order
    const items = screen.getAllByRole("listitem");
    expect(items[0]).toHaveTextContent("Spinach"); // Urgent first
    expect(items[1]).toHaveTextContent("Tomatoes"); // High second
    expect(items[2]).toHaveTextContent("Onions"); // Medium third
    expect(items[3]).toHaveTextContent("Carrots"); // Low last
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
});
