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
});
