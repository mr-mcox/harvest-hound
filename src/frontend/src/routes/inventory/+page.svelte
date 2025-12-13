<script lang="ts">
  type Priority = "Low" | "Medium" | "High" | "Urgent";
  type ClaimFilter = "All" | "Unclaimed only" | "Claimed only";

  interface RecipeClaimSummary {
    recipe_id: string;
    recipe_name: string;
    quantity: number;
    unit: string;
  }

  interface InventoryItem {
    id: number;
    ingredient_name: string;
    quantity: number;
    available: number;
    unit: string;
    priority: Priority;
    portion_size: string | null;
    added_at: string;
    claims: RecipeClaimSummary[];
  }

  let items = $state<InventoryItem[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let claimFilter = $state<ClaimFilter>("All");
  let claimsPopoverItemId = $state<number | null>(null);
  let editingItemId = $state<number | null>(null);
  let editingQuantity = $state<number>(0);
  let editingPriorityItemId = $state<number | null>(null);
  let editingPriority = $state<Priority>("Low");

  const priorityOrder: Record<Priority, number> = {
    Urgent: 4,
    High: 3,
    Medium: 2,
    Low: 1,
  };

  let sortedItems = $derived(
    [...items]
      .filter((item) => {
        // Existing filter: quantity > 0
        if (item.quantity <= 0) return false;

        // New claim filter
        if (claimFilter === "Unclaimed only") {
          return item.available > 0;
        } else if (claimFilter === "Claimed only") {
          return item.claims.length > 0;
        }
        return true; // "All"
      })
      .sort((a, b) => priorityOrder[b.priority] - priorityOrder[a.priority])
  );

  async function fetchInventory() {
    loading = true;
    error = null;

    try {
      const response = await fetch("/api/inventory/with-claims");

      if (!response.ok) {
        throw new Error(`Failed to load: ${response.status}`);
      }

      items = await response.json();
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to load inventory";
    } finally {
      loading = false;
    }
  }

  function getAvailabilityShade(available: number, total: number): string {
    if (available === total) {
      return "text-surface-900-100"; // Unclaimed - normal/black
    } else if (available === 0) {
      return "text-surface-400"; // Fully claimed - light grey
    } else {
      return "text-surface-600"; // Partially claimed - grey
    }
  }

  function formatAmount(item: InventoryItem): string {
    const baseAmount = `${item.quantity} ${item.unit}`;
    if (item.available === item.quantity) {
      return baseAmount; // Unclaimed
    } else if (item.available === 0) {
      return `${baseAmount} (0 avail)`; // Fully claimed
    } else {
      return `${baseAmount} (${item.available} avail)`; // Partially claimed
    }
  }

  async function deleteItem(itemId: number) {
    const itemToDelete = items.find((item) => item.id === itemId);
    if (!itemToDelete) return;

    // Optimistic update: remove from items immediately
    items = items.filter((item) => item.id !== itemId);

    try {
      const response = await fetch(`/api/inventory/${itemId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`Failed to delete: ${response.status}`);
      }
    } catch (e) {
      // Rollback: restore the item on error
      items = [...items, itemToDelete];
      error = e instanceof Error ? e.message : "Failed to delete item";

      setTimeout(() => {
        error = null;
      }, 3000);
    }
  }

  function startEditingQuantity(itemId: number, currentQuantity: number) {
    editingItemId = itemId;
    editingQuantity = currentQuantity;
  }

  function cancelEditing() {
    editingItemId = null;
    editingQuantity = 0;
  }

  async function saveQuantity(itemId: number) {
    const item = items.find((i) => i.id === itemId);
    if (!item) return;

    const previousQuantity = item.quantity;
    const newQuantity = editingQuantity; // Capture value before cancelEditing()

    // Validate quantity > 0
    if (newQuantity <= 0) {
      cancelEditing();
      return;
    }

    // Optimistic update
    item.quantity = newQuantity;
    items = [...items];
    cancelEditing();

    try {
      const response = await fetch(`/api/inventory/${itemId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantity: newQuantity }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update: ${response.status}`);
      }
    } catch (e) {
      // Rollback on error
      item.quantity = previousQuantity;
      items = [...items];
      error = e instanceof Error ? e.message : "Failed to update quantity";

      setTimeout(() => {
        error = null;
      }, 3000);
    }
  }

  function startEditingPriority(itemId: number, currentPriority: Priority) {
    editingPriorityItemId = itemId;
    editingPriority = currentPriority;
  }

  function cancelPriorityEditing() {
    editingPriorityItemId = null;
  }

  async function savePriority(itemId: number, newPriority: Priority) {
    const item = items.find((i) => i.id === itemId);
    if (!item) return;

    const previousPriority = item.priority;

    // Optimistic update
    item.priority = newPriority;
    items = [...items];
    cancelPriorityEditing();

    try {
      const response = await fetch(`/api/inventory/${itemId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ priority: newPriority }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update: ${response.status}`);
      }
    } catch (e) {
      // Rollback on error
      item.priority = previousPriority;
      items = [...items];
      error = e instanceof Error ? e.message : "Failed to update priority";

      setTimeout(() => {
        error = null;
      }, 3000);
    }
  }

  $effect(() => {
    fetchInventory();
  });
</script>

<main class="p-10 space-y-6 max-w-3xl mx-auto">
  <div class="flex items-center justify-between">
    <h1 class="h1">Inventory</h1>
    <a href="/inventory/import" class="btn preset-filled-primary-500"
      >Import Ingredients</a
    >
  </div>

  <div class="flex items-center gap-2">
    <label for="claim-filter" class="text-sm font-medium">Filter:</label>
    <select
      id="claim-filter"
      bind:value={claimFilter}
      class="px-3 py-2 border border-surface-500 rounded text-sm"
    >
      <option value="All">All</option>
      <option value="Unclaimed only">Unclaimed only</option>
      <option value="Claimed only">Claimed only</option>
    </select>
  </div>

  {#if error}
    <div class="card preset-outlined-error-500 p-4">
      <p class="text-error-500">{error}</p>
    </div>
  {:else if loading}
    <div class="card preset-outlined-surface-500 p-4">
      <p class="text-surface-600-400">Loading inventory...</p>
    </div>
  {:else if sortedItems.length === 0}
    <div class="card preset-outlined-surface-500 p-8 text-center">
      <p class="text-surface-600-400">No items in inventory</p>
      <p class="text-surface-500 text-sm mt-2">
        Import ingredients from your CSA delivery to get started.
      </p>
    </div>
  {:else}
    <div class="card preset-outlined-surface-500 overflow-x-auto">
      <table class="table-auto w-full">
        <thead>
          <tr class="border-b border-surface-500/20">
            <th class="text-left p-4 font-semibold">Ingredient</th>
            <th class="text-left p-4 font-semibold">Amount</th>
            <th class="text-left p-4 font-semibold">Priority</th>
            <th class="text-left p-4 font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each sortedItems as item}
            <tr class="border-b border-surface-500/20 last:border-b-0">
              <td class="p-4 font-medium relative">
                <div class="flex items-center gap-2">
                  <span>{item.ingredient_name}</span>
                  {#if item.claims.length > 0}
                    <span
                      class="text-primary-500 cursor-help relative inline-flex items-center"
                      onmouseenter={() => (claimsPopoverItemId = item.id)}
                      onmouseleave={() => (claimsPopoverItemId = null)}
                      role="button"
                      tabindex="0"
                      aria-label="View {item.claims.length} claiming recipe{item.claims
                        .length > 1
                        ? 's'
                        : ''}"
                    >
                      🔗
                      {#if claimsPopoverItemId === item.id}
                        <div
                          class="absolute left-6 top-0 z-10 w-64 bg-surface-100-900 border border-surface-500 rounded-lg shadow-lg p-3 space-y-2"
                          role="tooltip"
                          aria-label="Claiming recipes"
                        >
                          <h3 class="font-semibold text-sm text-surface-900-100">
                            Claimed by:
                          </h3>
                          {#each item.claims as claim}
                            <div class="text-sm">
                              <a
                                href="/recipes/{claim.recipe_id}"
                                class="text-primary-500 hover:text-primary-600 transition-colors block"
                                aria-label="View recipe {claim.recipe_name}"
                              >
                                {claim.recipe_name}
                              </a>
                              <span class="text-surface-500 text-xs">
                                {claim.quantity}
                                {claim.unit}
                              </span>
                            </div>
                          {/each}
                        </div>
                      {/if}
                    </span>
                  {/if}
                </div>
              </td>
              <td class="p-4">
                {#if editingItemId === item.id}
                  <input
                    type="number"
                    step="1"
                    class="w-20 px-2 py-1 border border-primary-500 rounded"
                    bind:value={editingQuantity}
                    onblur={() => saveQuantity(item.id)}
                    onkeydown={(e) => {
                      if (e.key === "Enter") {
                        saveQuantity(item.id);
                      } else if (e.key === "Escape") {
                        cancelEditing();
                      }
                    }}
                    autofocus
                  />
                {:else}
                  <button
                    type="button"
                    class={`hover:text-primary-500 transition-colors cursor-pointer ${getAvailabilityShade(item.available, item.quantity)}`}
                    onclick={() => startEditingQuantity(item.id, item.quantity)}
                  >
                    {formatAmount(item)}
                  </button>
                {/if}
              </td>
              <td class="p-4">
                {#if editingPriorityItemId === item.id}
                  <select
                    class="px-2 py-1 border border-primary-500 rounded text-sm"
                    bind:value={editingPriority}
                    onchange={() => savePriority(item.id, editingPriority)}
                    onblur={cancelPriorityEditing}
                    autofocus
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Urgent">Urgent</option>
                  </select>
                {:else}
                  <button
                    type="button"
                    class="text-sm hover:opacity-75 transition-opacity cursor-pointer"
                    onclick={() => startEditingPriority(item.id, item.priority)}
                  >
                    {item.priority}
                  </button>
                {/if}
              </td>
              <td class="p-4">
                <button
                  type="button"
                  class="text-error-500 hover:text-error-600 transition-colors"
                  aria-label="Delete {item.ingredient_name}"
                  title="Delete item"
                  onclick={() => deleteItem(item.id)}
                >
                  <svg
                    class="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</main>
