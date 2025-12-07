<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";

  interface Session {
    id: string;
    name: string;
    created_at: string;
  }

  let session: Session | null = $state(null);
  let loading = $state(true);
  let error = $state("");

  async function loadSession() {
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}`);
    if (response.ok) {
      session = await response.json();
    } else if (response.status === 404) {
      error = "Session not found";
    } else {
      error = "Failed to load session";
    }
    loading = false;
  }

  onMount(loadSession);
</script>

<main class="p-10 space-y-6 max-w-2xl mx-auto">
  <a href="/" class="text-sm text-surface-600-400 hover:underline"
    >&larr; Back to Home</a
  >

  {#if loading}
    <p class="text-surface-600-400">Loading session...</p>
  {:else if error}
    <div class="card preset-outlined-error-500 p-6">
      <p>{error}</p>
    </div>
  {:else if session}
    <div class="flex items-center justify-between">
      <h1 class="h1">{session.name || "Untitled Session"}</h1>
    </div>

    <p class="text-sm text-surface-600-400">
      Created {new Date(session.created_at).toLocaleDateString()}
    </p>

    <!-- Placeholder for Phase 3: Meal Criteria -->
    <div class="card preset-outlined-surface-500 p-6 space-y-4">
      <h2 class="h3">Meal Criteria</h2>
      <p class="text-surface-600-400">
        Add meal criteria to define your planning constraints.
      </p>
      <p class="text-sm text-surface-500">Coming in Phase 3...</p>
    </div>
  {/if}
</main>
