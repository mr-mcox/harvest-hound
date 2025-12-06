import { render, screen, fireEvent, waitFor } from "@testing-library/svelte";
import { describe, it, expect, vi, beforeEach } from "vitest";
import GroceryStoreTable from "./GroceryStoreTable.svelte";

describe("GroceryStoreTable", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders list of stores", () => {
    render(GroceryStoreTable, {
      props: {
        stores: [
          {
            id: 1,
            name: "Cub Foods",
            description: "Weekly groceries",
            created_at: "2025-01-01T00:00:00Z",
          },
          {
            id: 2,
            name: "Costco",
            description: "Bulk items",
            created_at: "2025-01-02T00:00:00Z",
          },
        ],
      },
    });

    expect(screen.getByText("Cub Foods")).toBeInTheDocument();
    expect(screen.getByText("Costco")).toBeInTheDocument();
  });

  it("add button opens form", async () => {
    render(GroceryStoreTable, {
      props: {
        stores: [],
      },
    });

    const addButton = screen.getByRole("button", { name: /add/i });
    await fireEvent.click(addButton);

    expect(screen.getByPlaceholderText(/store name/i)).toBeInTheDocument();
  });

  it("delete shows confirmation", async () => {
    const mockOnDelete = vi.fn();

    render(GroceryStoreTable, {
      props: {
        stores: [
          {
            id: 1,
            name: "Test Store",
            description: "Test",
            created_at: "2025-01-01T00:00:00Z",
          },
        ],
        onDelete: mockOnDelete,
      },
    });

    const deleteButton = screen.getByRole("button", { name: /delete/i });
    await fireEvent.click(deleteButton);

    // Should show confirmation
    expect(screen.getByText(/confirm/i)).toBeInTheDocument();
  });
});
