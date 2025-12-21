<script lang="ts">
  interface ShoppingListItem {
    ingredient_name: string;
    total_quantity: string;
    purchase_likelihood: number;
    used_in_recipes: string[];
  }

  interface ShoppingListResponse {
    grocery_items: ShoppingListItem[];
    pantry_staples: ShoppingListItem[];
  }

  interface Props {
    shoppingList: ShoppingListResponse | null;
    loading: boolean;
    error: string;
    sessionId: string;
    initialSelections?: Record<string, boolean>;
  }

  let {
    shoppingList,
    loading,
    error,
    sessionId,
    initialSelections = {},
  }: Props = $props();

  let selections: Map<string, boolean> = $state(new Map());
  let filterCheckedOnly: boolean = $state(false);
  let copySuccess: boolean = $state(false);

  // Review state
  let reviewedAt: string | null = $state(null);
  let reviewing: boolean = $state(false);
  let reviewSuccess: boolean = $state(false);

  // Initialize selections from props
  $effect(() => {
    if (initialSelections) {
      selections = new Map(Object.entries(initialSelections));
    }
  });

  function isChecked(ingredientName: string): boolean {
    return selections.get(ingredientName) ?? false;
  }

  // Compute checked count
  let checkedCount = $derived(Array.from(selections.values()).filter(Boolean).length);

  // Compute filtered lists
  let visibleGroceryItems = $derived(
    filterCheckedOnly
      ? (shoppingList?.grocery_items ?? []).filter((item) =>
          isChecked(item.ingredient_name)
        )
      : (shoppingList?.grocery_items ?? [])
  );

  let visiblePantryStaples = $derived(
    filterCheckedOnly
      ? (shoppingList?.pantry_staples ?? []).filter((item) =>
          isChecked(item.ingredient_name)
        )
      : (shoppingList?.pantry_staples ?? [])
  );

  // Get all checked items for copy functionality
  function getCheckedItems(): ShoppingListItem[] {
    const allItems = [
      ...(shoppingList?.grocery_items ?? []),
      ...(shoppingList?.pantry_staples ?? []),
    ];
    return allItems.filter((item) => isChecked(item.ingredient_name));
  }

  async function copyCheckedItems() {
    const checkedItems = getCheckedItems();
    const text = checkedItems
      .map((item) => `${item.ingredient_name} ${item.total_quantity}`)
      .join("\n");

    try {
      await navigator.clipboard.writeText(text);
      copySuccess = true;
      setTimeout(() => {
        copySuccess = false;
      }, 2000);
    } catch (err) {
      console.error("Failed to copy to clipboard:", err);
    }
  }

  function toggleFilter() {
    filterCheckedOnly = !filterCheckedOnly;
  }

  async function toggleSelection(ingredientName: string) {
    const newChecked = !isChecked(ingredientName);

    // Optimistic update
    selections.set(ingredientName, newChecked);
    selections = new Map(selections);

    try {
      const response = await fetch(
        `/api/sessions/${sessionId}/shopping-list/selections`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ingredient_name: ingredientName,
            checked: newChecked,
          }),
        }
      );

      if (!response.ok) {
        // Rollback on failure
        selections.set(ingredientName, !newChecked);
        selections = new Map(selections);
        console.error("Failed to update selection");
      }
    } catch (err) {
      // Rollback on error
      selections.set(ingredientName, !newChecked);
      selections = new Map(selections);
      console.error("Failed to update selection:", err);
    }
  }

  async function markAsReviewed() {
    reviewing = true;

    try {
      const response = await fetch(`/api/sessions/${sessionId}/shopping-list/review`, {
        method: "POST",
      });

      if (response.ok) {
        const data = await response.json();
        reviewedAt = data.reviewed_at;
        reviewSuccess = true;
        setTimeout(() => {
          reviewSuccess = false;
        }, 3000);
      } else {
        console.error("Failed to mark as reviewed");
      }
    } catch (err) {
      console.error("Failed to mark as reviewed:", err);
    } finally {
      reviewing = false;
    }
  }

  function formatReviewDate(isoDate: string): string {
    const date = new Date(isoDate);
    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }
</script>

{#if shoppingList && (shoppingList.grocery_items.length > 0 || shoppingList.pantry_staples.length > 0)}
  <div class="card preset-outlined-secondary-500 p-6 space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="h4">Shopping List</h3>
      <div class="flex items-center gap-2">
        {#if checkedCount > 0}
          <button
            type="button"
            onclick={copyCheckedItems}
            class="btn btn-sm preset-outlined-primary-500"
          >
            {#if copySuccess}
              Copied!
            {:else}
              Copy Checked ({checkedCount})
            {/if}
          </button>
        {/if}
        <button
          type="button"
          onclick={toggleFilter}
          class="btn btn-sm {filterCheckedOnly
            ? 'preset-filled-primary-500'
            : 'preset-outlined-surface-500'}"
        >
          {filterCheckedOnly ? "Items to Buy" : "All Items"}
        </button>
      </div>
    </div>

    {#if loading}
      <p class="text-surface-600-400 text-sm">Loading shopping list...</p>
    {:else if error}
      <div class="card preset-outlined-error-500 p-4">
        <p class="text-sm text-error-500">{error}</p>
      </div>
    {:else}
      <!-- Grocery Items (high confidence) -->
      {#if visibleGroceryItems.length > 0}
        <div class="space-y-2">
          <h4 class="font-semibold text-surface-700-300">
            Grocery Items
            <span class="text-sm font-normal text-surface-500">
              (High confidence - definitely need to buy)
            </span>
          </h4>
          <ul class="space-y-2">
            {#each visibleGroceryItems as item}
              {@const checked = isChecked(item.ingredient_name)}
              <li
                class="p-3 rounded bg-surface-100-900 transition-opacity {checked
                  ? 'opacity-60 bg-success-500/10'
                  : ''}"
              >
                <div class="flex items-start gap-3">
                  <input
                    type="checkbox"
                    {checked}
                    onchange={() => toggleSelection(item.ingredient_name)}
                    class="mt-1 w-5 h-5 rounded border-2 border-surface-400 text-primary-500 focus:ring-primary-500 cursor-pointer"
                  />
                  <div class="flex-1">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <span class="font-medium {checked ? 'line-through' : ''}"
                          >{item.ingredient_name}</span
                        >
                        <span class="text-surface-600-400 ml-2">
                          {item.total_quantity}
                        </span>
                      </div>
                      <span
                        class="text-xs px-2 py-1 rounded bg-primary-500/20 text-primary-500"
                      >
                        {Math.round(item.purchase_likelihood * 100)}% confidence
                      </span>
                    </div>
                    {#if item.used_in_recipes.length > 0}
                      <div class="text-xs text-surface-500 mt-1">
                        Used in: {item.used_in_recipes.join(", ")}
                      </div>
                    {/if}
                  </div>
                </div>
              </li>
            {/each}
          </ul>
        </div>
      {/if}

      <!-- Pantry Staples (low confidence) -->
      {#if visiblePantryStaples.length > 0}
        <div class="space-y-2 pt-4 border-t border-surface-300-700">
          <h4 class="font-semibold text-surface-700-300">
            Pantry Staples to Verify
            <span class="text-sm font-normal text-surface-500">
              (Lower confidence - check if you have these)
            </span>
          </h4>
          <ul class="space-y-2">
            {#each visiblePantryStaples as item}
              {@const checked = isChecked(item.ingredient_name)}
              <li
                class="p-3 rounded bg-surface-100-900 transition-opacity {checked
                  ? 'opacity-60 bg-success-500/10'
                  : 'opacity-75'}"
              >
                <div class="flex items-start gap-3">
                  <input
                    type="checkbox"
                    {checked}
                    onchange={() => toggleSelection(item.ingredient_name)}
                    class="mt-1 w-5 h-5 rounded border-2 border-surface-400 text-primary-500 focus:ring-primary-500 cursor-pointer"
                  />
                  <div class="flex-1">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <span class="font-medium {checked ? 'line-through' : ''}"
                          >{item.ingredient_name}</span
                        >
                        <span class="text-surface-600-400 ml-2">
                          {item.total_quantity}
                        </span>
                      </div>
                      <span
                        class="text-xs px-2 py-1 rounded bg-surface-500/20 text-surface-500"
                      >
                        {Math.round(item.purchase_likelihood * 100)}% confidence
                      </span>
                    </div>
                    {#if item.used_in_recipes.length > 0}
                      <div class="text-xs text-surface-500 mt-1">
                        Used in: {item.used_in_recipes.join(", ")}
                      </div>
                    {/if}
                  </div>
                </div>
              </li>
            {/each}
          </ul>
        </div>
      {/if}

      <!-- Empty state when filtering -->
      {#if filterCheckedOnly && visibleGroceryItems.length === 0 && visiblePantryStaples.length === 0}
        <p class="text-surface-500 text-sm italic">
          No items checked. Check items you need to buy, then use this filter to see
          only those items.
        </p>
      {/if}

      <!-- Review action -->
      <div
        class="pt-4 border-t border-surface-300-700 flex items-center justify-between"
      >
        <div class="text-sm text-surface-500">
          {#if reviewSuccess}
            <span class="text-success-500">Shopping list reviewed!</span>
          {:else if reviewedAt}
            Last reviewed: {formatReviewDate(reviewedAt)}
          {:else}
            Mark as reviewed when done shopping
          {/if}
        </div>
        <button
          type="button"
          onclick={markAsReviewed}
          disabled={reviewing}
          class="btn btn-sm preset-filled-secondary-500"
        >
          {#if reviewing}
            Reviewing...
          {:else if reviewedAt}
            Update Review
          {:else}
            Mark as Reviewed
          {/if}
        </button>
      </div>
    {/if}
  </div>
{/if}
