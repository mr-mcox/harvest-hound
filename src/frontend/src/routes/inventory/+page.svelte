<script lang="ts">
  type Priority = "Low" | "Medium" | "High" | "Urgent";

  interface InventoryItem {
    id: number;
    ingredient_name: string;
    quantity: number;
    unit: string;
    priority: Priority;
    portion_size: string | null;
    added_at: string;
  }

  let items = $state<InventoryItem[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  const priorityOrder: Record<Priority, number> = {
    Urgent: 4,
    High: 3,
    Medium: 2,
    Low: 1,
  };

  let sortedItems = $derived(
    [...items].sort((a, b) => priorityOrder[b.priority] - priorityOrder[a.priority])
  );

  async function fetchInventory() {
    loading = true;
    error = null;

    try {
      const response = await fetch("/api/inventory");

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
    <div class="card preset-outlined-surface-500">
      <ul class="divide-y divide-surface-500/20">
        {#each sortedItems as item}
          <li class="flex items-center justify-between p-4">
            <div class="flex-1">
              <span class="font-medium">{item.ingredient_name}</span>
              <span class="text-surface-600-400 ml-2">
                {item.quantity}
                {item.unit}
                {#if item.portion_size}
                  ({item.portion_size} portions)
                {/if}
              </span>
            </div>
            <span class={`text-sm ${getPriorityColor(item.priority)}`}>
              {item.priority}
            </span>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
</main>
