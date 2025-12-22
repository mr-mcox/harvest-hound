import { render, screen, fireEvent, waitFor } from "@testing-library/svelte";
import { describe, it, expect, vi, beforeEach } from "vitest";
import ShoppingList from "./ShoppingList.svelte";

describe("ShoppingList", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const mockShoppingList = {
    grocery_items: [
      {
        ingredient_name: "Chicken Breast",
        total_quantity: "2 lbs",
        purchase_likelihood: 0.9,
        used_in_recipes: ["Chicken Stir Fry"],
      },
      {
        ingredient_name: "Bell Peppers",
        total_quantity: "3",
        purchase_likelihood: 0.7,
        used_in_recipes: ["Chicken Stir Fry", "Fajitas"],
      },
    ],
    pantry_staples: [
      {
        ingredient_name: "Olive Oil",
        total_quantity: "2 tbsp",
        purchase_likelihood: 0.2,
        used_in_recipes: ["Chicken Stir Fry"],
      },
    ],
  };

  it("renders grocery items and pantry staples", () => {
    render(ShoppingList, {
      props: {
        shoppingList: mockShoppingList,
        loading: false,
        error: "",
        sessionId: "test-session-id",
      },
    });

    expect(screen.getByText("Chicken Breast")).toBeInTheDocument();
    expect(screen.getByText("Bell Peppers")).toBeInTheDocument();
    expect(screen.getByText("Olive Oil")).toBeInTheDocument();
  });

  it("renders checkboxes for each item", () => {
    render(ShoppingList, {
      props: {
        shoppingList: mockShoppingList,
        loading: false,
        error: "",
        sessionId: "test-session-id",
      },
    });

    const checkboxes = screen.getAllByRole("checkbox");
    // 2 grocery items + 1 pantry staple = 3 checkboxes
    expect(checkboxes).toHaveLength(3);
  });

  it("calls API when checkbox is toggled", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          ingredient_name: "Chicken Breast",
          checked: true,
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(ShoppingList, {
      props: {
        shoppingList: mockShoppingList,
        loading: false,
        error: "",
        sessionId: "test-session-id",
      },
    });

    const checkboxes = screen.getAllByRole("checkbox");
    await fireEvent.click(checkboxes[0]);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/sessions/test-session-id/shopping-list/selections",
        expect.objectContaining({
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ingredient_name: "Chicken Breast",
            checked: true,
          }),
        })
      );
    });
  });

  it("shows checked items with visual distinction", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          ingredient_name: "Chicken Breast",
          checked: true,
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(ShoppingList, {
      props: {
        shoppingList: mockShoppingList,
        loading: false,
        error: "",
        sessionId: "test-session-id",
        initialSelections: { "Chicken Breast": true },
      },
    });

    // The checked item should have the checked checkbox
    const checkboxes = screen.getAllByRole("checkbox") as HTMLInputElement[];
    expect(checkboxes[0].checked).toBe(true);
    expect(checkboxes[1].checked).toBe(false);
  });

  describe("Filter toggle", () => {
    it("shows filter toggle button", () => {
      render(ShoppingList, {
        props: {
          shoppingList: mockShoppingList,
          loading: false,
          error: "",
          sessionId: "test-session-id",
        },
      });

      expect(screen.getByRole("button", { name: /all items/i })).toBeInTheDocument();
    });

    it("filters to show only checked items when toggled", async () => {
      render(ShoppingList, {
        props: {
          shoppingList: mockShoppingList,
          loading: false,
          error: "",
          sessionId: "test-session-id",
          initialSelections: { "Chicken Breast": true },
        },
      });

      // All items visible initially
      expect(screen.getByText("Chicken Breast")).toBeInTheDocument();
      expect(screen.getByText("Bell Peppers")).toBeInTheDocument();
      expect(screen.getByText("Olive Oil")).toBeInTheDocument();

      // Click filter toggle
      const filterButton = screen.getByRole("button", { name: /all items/i });
      await fireEvent.click(filterButton);

      // Only checked item visible
      expect(screen.getByText("Chicken Breast")).toBeInTheDocument();
      expect(screen.queryByText("Bell Peppers")).not.toBeInTheDocument();
      expect(screen.queryByText("Olive Oil")).not.toBeInTheDocument();
    });

    it("toggles back to show all items", async () => {
      render(ShoppingList, {
        props: {
          shoppingList: mockShoppingList,
          loading: false,
          error: "",
          sessionId: "test-session-id",
          initialSelections: { "Chicken Breast": true },
        },
      });

      // Toggle to filtered view
      const filterButton = screen.getByRole("button", { name: /all items/i });
      await fireEvent.click(filterButton);

      // Toggle back to all items
      const itemsToBuyButton = screen.getByRole("button", { name: /items to buy/i });
      await fireEvent.click(itemsToBuyButton);

      // All items visible again
      expect(screen.getByText("Chicken Breast")).toBeInTheDocument();
      expect(screen.getByText("Bell Peppers")).toBeInTheDocument();
      expect(screen.getByText("Olive Oil")).toBeInTheDocument();
    });
  });

  describe("Copy checked items", () => {
    it("shows copy button only when items are checked", async () => {
      render(ShoppingList, {
        props: {
          shoppingList: mockShoppingList,
          loading: false,
          error: "",
          sessionId: "test-session-id",
          initialSelections: {},
        },
      });

      // No items checked - button should not be visible
      expect(
        screen.queryByRole("button", { name: /copy checked/i })
      ).not.toBeInTheDocument();
    });

    it("shows copy button when items are checked", async () => {
      render(ShoppingList, {
        props: {
          shoppingList: mockShoppingList,
          loading: false,
          error: "",
          sessionId: "test-session-id",
          initialSelections: { "Chicken Breast": true },
        },
      });

      expect(screen.getByRole("button", { name: /copy checked/i })).toBeInTheDocument();
    });

    it("copies checked items to clipboard in correct format", async () => {
      const writeTextMock = vi.fn().mockResolvedValue(undefined);
      Object.assign(navigator, {
        clipboard: { writeText: writeTextMock },
      });

      render(ShoppingList, {
        props: {
          shoppingList: mockShoppingList,
          loading: false,
          error: "",
          sessionId: "test-session-id",
          initialSelections: { "Chicken Breast": true, "Olive Oil": true },
        },
      });

      const copyButton = screen.getByRole("button", { name: /copy checked/i });
      await fireEvent.click(copyButton);

      expect(writeTextMock).toHaveBeenCalledWith(
        "Chicken Breast 2 lbs\nOlive Oil 2 tbsp"
      );
    });

    it("shows success feedback after copying", async () => {
      const writeTextMock = vi.fn().mockResolvedValue(undefined);
      Object.assign(navigator, {
        clipboard: { writeText: writeTextMock },
      });

      render(ShoppingList, {
        props: {
          shoppingList: mockShoppingList,
          loading: false,
          error: "",
          sessionId: "test-session-id",
          initialSelections: { "Chicken Breast": true },
        },
      });

      const copyButton = screen.getByRole("button", { name: /copy checked/i });
      await fireEvent.click(copyButton);

      await waitFor(() => {
        expect(screen.getByText(/copied/i)).toBeInTheDocument();
      });
    });
  });
});
