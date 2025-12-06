<script lang="ts">
  import ConfigTextArea from "$lib/components/ConfigTextArea.svelte";
  import GroceryStoreTable from "$lib/components/GroceryStoreTable.svelte";

  // API response types
  interface SingletonConfig {
    content: string;
    updated_at: string;
  }

  interface GroceryStore {
    id: number;
    name: string;
    description: string;
    created_at: string;
  }

  // State
  let householdProfile = $state<SingletonConfig | null>(null);
  let pantry = $state<SingletonConfig | null>(null);
  let groceryStores = $state<GroceryStore[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  // Load data on mount
  $effect(() => {
    loadData();
  });

  async function loadData() {
    loading = true;
    error = null;

    try {
      const [profileRes, pantryRes, storesRes] = await Promise.all([
        fetch("/api/config/household-profile"),
        fetch("/api/config/pantry"),
        fetch("/api/config/grocery-stores"),
      ]);

      if (!profileRes.ok || !pantryRes.ok || !storesRes.ok) {
        throw new Error("Failed to load settings");
      }

      householdProfile = await profileRes.json();
      pantry = await pantryRes.json();
      groceryStores = await storesRes.json();
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to load settings";
    } finally {
      loading = false;
    }
  }

  // Grocery store CRUD handlers
  async function addStore(name: string, description: string) {
    const response = await fetch("/api/config/grocery-stores", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, description }),
    });
    if (!response.ok) {
      throw new Error("Failed to add store");
    }
    const newStore = await response.json();
    groceryStores = [...groceryStores, newStore];
  }

  async function updateStore(id: number, name: string, description: string) {
    const response = await fetch(`/api/config/grocery-stores/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, description }),
    });
    if (!response.ok) {
      throw new Error("Failed to update store");
    }
    const updatedStore = await response.json();
    groceryStores = groceryStores.map((s) => (s.id === id ? updatedStore : s));
  }

  async function deleteStore(id: number) {
    const response = await fetch(`/api/config/grocery-stores/${id}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Failed to delete store");
    }
    groceryStores = groceryStores.filter((s) => s.id !== id);
  }
</script>

<main class="p-10 space-y-8 max-w-3xl mx-auto">
  <div class="flex items-center justify-between">
    <h1 class="h1">Settings</h1>
    <a href="/" class="btn preset-outlined-surface-500">Back to Home</a>
  </div>

  {#if loading}
    <div class="card preset-outlined-surface-500 p-4">
      <p class="text-surface-500">Loading settings...</p>
    </div>
  {:else if error}
    <div class="card preset-outlined-error-500 p-4">
      <p>{error}</p>
      <button
        type="button"
        class="btn preset-outlined-surface-500 mt-2"
        onclick={loadData}
      >
        Retry
      </button>
    </div>
  {:else}
    <!-- Household Profile Section -->
    <section class="space-y-4">
      <h2 class="h2">Household Profile</h2>
      <p class="text-surface-600-400">
        Describe your family's cooking context for better recipe suggestions.
      </p>
      <ConfigTextArea
        label="Household Profile"
        apiEndpoint="/api/config/household-profile"
        initialContent={householdProfile?.content ?? ""}
      />
    </section>

    <!-- Pantry Section -->
    <section class="space-y-4">
      <h2 class="h2">Pantry</h2>
      <p class="text-surface-600-400">
        List your pantry staples that are always available (salt, pepper, olive oil,
        etc.).
      </p>
      <ConfigTextArea
        label="Pantry"
        apiEndpoint="/api/config/pantry"
        initialContent={pantry?.content ?? ""}
      />
    </section>
  {/if}

  <!-- Grocery Stores Section -->
  <section class="space-y-4">
    <h2 class="h2">Grocery Stores</h2>
    <p class="text-surface-600-400">
      Manage your shopping destinations for shopping list claims.
    </p>
    {#if !loading && !error}
      <GroceryStoreTable
        stores={groceryStores}
        onAdd={addStore}
        onUpdate={updateStore}
        onDelete={deleteStore}
      />
    {/if}
  </section>
</main>
