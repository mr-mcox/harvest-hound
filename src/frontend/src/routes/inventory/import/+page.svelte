<script lang="ts">
  import { goto } from "$app/navigation";

  type Priority = "Low" | "Medium" | "High" | "Urgent";

  interface ParsedIngredient {
    ingredient_name: string;
    quantity: number;
    unit: string;
    priority: Priority;
    portion_size: string | null;
  }

  let freeText = $state("");
  let configurationInstructions = $state("");
  let pendingItems = $state<ParsedIngredient[]>([]); // Lost on refresh
  let parsing = $state(false);
  let approving = $state(false);
  let error = $state<string | null>(null);

  async function parseIngredients() {
    if (!freeText.trim()) return;

    parsing = true;
    error = null;

    try {
      const response = await fetch("/api/inventory/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          free_text: freeText,
          configuration_instructions: configurationInstructions || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to parse: ${response.status}`);
      }

      const data = await response.json();

      pendingItems = [...pendingItems, ...data.ingredients];
      freeText = "";
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to parse ingredients";
    } finally {
      parsing = false;
    }
  }

  function deleteItem(index: number) {
    pendingItems = pendingItems.filter((_, i) => i !== index);
  }

  async function approveAll() {
    if (pendingItems.length === 0) return;

    approving = true;
    error = null;

    try {
      const response = await fetch("/api/inventory/bulk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: pendingItems,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to save: ${response.status}`);
      }

      pendingItems = [];
      goto("/inventory");
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to save inventory";
    } finally {
      approving = false;
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
</script>

<main class="p-10 space-y-6 max-w-3xl mx-auto">
  <div class="flex items-center justify-between">
    <h1 class="h1">Import Ingredients</h1>
    <a href="/inventory" class="btn preset-outlined-surface-500">Back to Inventory</a>
  </div>

  <p class="text-surface-600-400">
    Paste your CSA delivery list or ingredient text below to parse and add to inventory.
  </p>

  {#if error}
    <div class="card preset-outlined-error-500 p-4">
      <p class="text-error-500">{error}</p>
    </div>
  {/if}

  <!-- Input Section -->
  <section class="space-y-4">
    <div class="space-y-2">
      <textarea
        class="textarea px-4 py-2 w-full"
        rows="6"
        placeholder="Paste your CSA delivery list here (e.g., 3 lbs tomatoes, 1 bunch kale...)"
        bind:value={freeText}
      ></textarea>
    </div>

    <div class="space-y-2">
      <textarea
        class="textarea px-4 py-2 w-full"
        rows="2"
        placeholder="Configuration instructions (optional, e.g., 'All frozen in 1lb portions')"
        bind:value={configurationInstructions}
      ></textarea>
    </div>

    <button
      type="button"
      class="btn preset-filled-primary-500"
      onclick={parseIngredients}
      disabled={parsing || !freeText.trim()}
    >
      {parsing ? "Parsing..." : "Parse Ingredients"}
    </button>
  </section>

  <!-- Pending Items Section -->
  {#if pendingItems.length > 0}
    <section class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="h3">Pending Items ({pendingItems.length})</h2>
        <button
          type="button"
          class="btn preset-filled-success-500"
          onclick={approveAll}
          disabled={approving}
        >
          {approving ? "Saving..." : "Approve All"}
        </button>
      </div>

      <div class="card preset-outlined-surface-500">
        <ul class="divide-y divide-surface-500/20">
          {#each pendingItems as item, index}
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
                <span class={`ml-2 text-sm ${getPriorityColor(item.priority)}`}>
                  {item.priority}
                </span>
              </div>
              <button
                type="button"
                class="btn preset-outlined-error-500 btn-sm"
                onclick={() => deleteItem(index)}
              >
                Delete
              </button>
            </li>
          {/each}
        </ul>
      </div>
    </section>
  {/if}
</main>
