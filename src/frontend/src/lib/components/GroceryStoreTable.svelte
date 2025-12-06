<script lang="ts">
  interface GroceryStore {
    id: number;
    name: string;
    description: string;
    created_at: string;
  }

  interface Props {
    stores: GroceryStore[];
    onAdd?: (name: string, description: string) => Promise<void>;
    onUpdate?: (id: number, name: string, description: string) => Promise<void>;
    onDelete?: (id: number) => Promise<void>;
  }

  let { stores, onAdd, onUpdate, onDelete }: Props = $props();

  // UI state
  let showAddForm = $state(false);
  let newName = $state("");
  let newDescription = $state("");
  let adding = $state(false);

  let editingId = $state<number | null>(null);
  let editName = $state("");
  let editDescription = $state("");
  let updating = $state(false);

  let confirmDeleteId = $state<number | null>(null);
  let deleting = $state(false);
  let deleteError = $state("");

  function startAdd() {
    showAddForm = true;
    newName = "";
    newDescription = "";
  }

  function cancelAdd() {
    showAddForm = false;
    newName = "";
    newDescription = "";
  }

  async function submitAdd() {
    if (!newName.trim() || !onAdd) return;
    adding = true;
    try {
      await onAdd(newName.trim(), newDescription.trim());
      cancelAdd();
    } finally {
      adding = false;
    }
  }

  function startEdit(store: GroceryStore) {
    editingId = store.id;
    editName = store.name;
    editDescription = store.description;
  }

  function cancelEdit() {
    editingId = null;
    editName = "";
    editDescription = "";
  }

  async function submitEdit() {
    if (!editName.trim() || editingId === null || !onUpdate) return;
    updating = true;
    try {
      await onUpdate(editingId, editName.trim(), editDescription.trim());
      cancelEdit();
    } finally {
      updating = false;
    }
  }

  function startDelete(id: number) {
    confirmDeleteId = id;
    deleteError = "";
  }

  function cancelDelete() {
    confirmDeleteId = null;
    deleteError = "";
  }

  async function confirmDelete() {
    if (confirmDeleteId === null || !onDelete) return;
    deleting = true;
    deleteError = "";
    try {
      await onDelete(confirmDeleteId);
      cancelDelete();
    } catch (e) {
      deleteError = e instanceof Error ? e.message : "Failed to delete";
    } finally {
      deleting = false;
    }
  }
</script>

<div class="space-y-4">
  <!-- Add button -->
  <div class="flex justify-end">
    <button
      type="button"
      class="btn preset-filled-primary-500"
      onclick={startAdd}
      disabled={showAddForm}
    >
      Add Store
    </button>
  </div>

  <!-- Add form -->
  {#if showAddForm}
    <div class="card preset-outlined-surface-500 p-4 space-y-3">
      <input
        type="text"
        class="input px-4 py-2 w-full"
        placeholder="Store name"
        bind:value={newName}
      />
      <input
        type="text"
        class="input px-4 py-2 w-full"
        placeholder="Description (optional)"
        bind:value={newDescription}
      />
      <div class="flex gap-2">
        <button
          type="button"
          class="btn preset-filled-primary-500"
          onclick={submitAdd}
          disabled={adding || !newName.trim()}
        >
          {adding ? "Adding..." : "Add"}
        </button>
        <button
          type="button"
          class="btn preset-outlined-surface-500"
          onclick={cancelAdd}
          disabled={adding}
        >
          Cancel
        </button>
      </div>
    </div>
  {/if}

  <!-- Store list -->
  {#if stores.length === 0}
    <p class="text-surface-500">No grocery stores configured.</p>
  {:else}
    <div class="space-y-2">
      {#each stores as store (store.id)}
        <div class="card preset-outlined-surface-500 p-4">
          {#if editingId === store.id}
            <!-- Edit mode -->
            <div class="space-y-3">
              <input
                type="text"
                class="input px-4 py-2 w-full"
                placeholder="Store name"
                bind:value={editName}
              />
              <input
                type="text"
                class="input px-4 py-2 w-full"
                placeholder="Description (optional)"
                bind:value={editDescription}
              />
              <div class="flex gap-2">
                <button
                  type="button"
                  class="btn preset-filled-primary-500"
                  onclick={submitEdit}
                  disabled={updating || !editName.trim()}
                >
                  {updating ? "Saving..." : "Save"}
                </button>
                <button
                  type="button"
                  class="btn preset-outlined-surface-500"
                  onclick={cancelEdit}
                  disabled={updating}
                >
                  Cancel
                </button>
              </div>
            </div>
          {:else if confirmDeleteId === store.id}
            <!-- Delete confirmation -->
            <div class="space-y-3">
              <p>Confirm delete "{store.name}"?</p>
              {#if deleteError}
                <p class="text-error-500">{deleteError}</p>
              {/if}
              <div class="flex gap-2">
                <button
                  type="button"
                  class="btn preset-filled-error-500"
                  onclick={confirmDelete}
                  disabled={deleting}
                >
                  {deleting ? "Deleting..." : "Delete"}
                </button>
                <button
                  type="button"
                  class="btn preset-outlined-surface-500"
                  onclick={cancelDelete}
                  disabled={deleting}
                >
                  Cancel
                </button>
              </div>
            </div>
          {:else}
            <!-- View mode -->
            <div class="flex justify-between items-start">
              <div>
                <h3 class="font-semibold">{store.name}</h3>
                {#if store.description}
                  <p class="text-surface-600-400">{store.description}</p>
                {/if}
              </div>
              <div class="flex gap-2">
                <button
                  type="button"
                  class="btn preset-outlined-surface-500"
                  onclick={() => startEdit(store)}
                >
                  Edit
                </button>
                <button
                  type="button"
                  class="btn preset-outlined-error-500"
                  onclick={() => startDelete(store.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
