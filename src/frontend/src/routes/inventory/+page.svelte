<script lang="ts">
  type Priority = "Low" | "Medium" | "High" | "Urgent";

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
      .filter((item) => item.quantity > 0)
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

  function getPriorityColor(priority: Priority): string {
    switch (priority) {
      case "Urgent":
        return "text-error-500";
      case "High":
        return "text-warning-500";
      case "Medium":
        return "text-primary-500";
      case "Low":
        return "text-surface-500";
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
            <th class="text-left p-4 font-semibold">Quantity</th>
            <th class="text-left p-4 font-semibold">Available</th>
            <th class="text-left p-4 font-semibold">Unit</th>
            <th class="text-left p-4 font-semibold">Priority</th>
            <th class="text-left p-4 font-semibold">Portion Size</th>
            <th class="text-left p-4 font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each sortedItems as item}
            <tr class="border-b border-surface-500/20 last:border-b-0">
              <td class="p-4 font-medium">{item.ingredient_name}</td>
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
                    class="hover:text-primary-500 transition-colors cursor-pointer"
                    onclick={() => startEditingQuantity(item.id, item.quantity)}
                  >
                    {item.quantity}
                  </button>
                {/if}
              </td>
              <td class="p-4 text-surface-600-400">
                {#if item.available === 0}
                  <span class="text-surface-500">Fully claimed</span>
                {:else}
                  {item.available}
                {/if}
              </td>
              <td class="p-4 text-surface-600-400">{item.unit}</td>
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
                    class={`text-sm ${getPriorityColor(item.priority)} hover:opacity-75 transition-opacity cursor-pointer`}
                    onclick={() => startEditingPriority(item.id, item.priority)}
                  >
                    {item.priority}
                  </button>
                {/if}
              </td>
              <td class="p-4 text-surface-600-400">
                {#if item.portion_size}
                  {item.portion_size} portions
                {:else}
                  —
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
