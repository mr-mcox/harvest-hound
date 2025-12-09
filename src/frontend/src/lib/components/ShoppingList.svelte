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
  }

  let { shoppingList, loading, error }: Props = $props();
</script>

{#if shoppingList && (shoppingList.grocery_items.length > 0 || shoppingList.pantry_staples.length > 0)}
  <div class="card preset-outlined-secondary-500 p-6 space-y-4">
    <h3 class="h4">Shopping List</h3>

    {#if loading}
      <p class="text-surface-600-400 text-sm">Loading shopping list...</p>
    {:else if error}
      <div class="card preset-outlined-error-500 p-4">
        <p class="text-sm text-error-500">{error}</p>
      </div>
    {:else}
      <!-- Grocery Items (high confidence) -->
      {#if shoppingList.grocery_items.length > 0}
        <div class="space-y-2">
          <h4 class="font-semibold text-surface-700-300">
            Grocery Items
            <span class="text-sm font-normal text-surface-500">
              (High confidence - definitely need to buy)
            </span>
          </h4>
          <ul class="space-y-2">
            {#each shoppingList.grocery_items as item}
              <li class="p-3 rounded bg-surface-100-900">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <span class="font-medium">{item.ingredient_name}</span>
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
              </li>
            {/each}
          </ul>
        </div>
      {/if}

      <!-- Pantry Staples (low confidence) -->
      {#if shoppingList.pantry_staples.length > 0}
        <div class="space-y-2 pt-4 border-t border-surface-300-700">
          <h4 class="font-semibold text-surface-700-300">
            Pantry Staples to Verify
            <span class="text-sm font-normal text-surface-500">
              (Lower confidence - check if you have these)
            </span>
          </h4>
          <ul class="space-y-2">
            {#each shoppingList.pantry_staples as item}
              <li class="p-3 rounded bg-surface-100-900 opacity-75">
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <span class="font-medium">{item.ingredient_name}</span>
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
              </li>
            {/each}
          </ul>
        </div>
      {/if}
    {/if}
  </div>
{/if}
