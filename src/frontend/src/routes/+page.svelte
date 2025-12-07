<script lang="ts">
  import { onMount } from "svelte";

  interface Session {
    id: string;
    name: string;
    created_at: string;
  }

  let sessions: Session[] = $state([]);
  let newSessionName = $state("");
  let loading = $state(true);

  // Generate default name: "Week of [prior Sunday]"
  function getDefaultSessionName(): string {
    const today = new Date();
    const dayOfWeek = today.getDay();
    const priorSunday = new Date(today);
    priorSunday.setDate(today.getDate() - dayOfWeek);
    return `Week of ${priorSunday.toLocaleDateString("en-US", { month: "short", day: "numeric" })}`;
  }

  async function loadSessions() {
    const response = await fetch("/api/sessions");
    if (response.ok) {
      sessions = await response.json();
    }
    loading = false;
  }

  async function createSession() {
    const name = newSessionName.trim() || getDefaultSessionName();
    const response = await fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    if (response.ok) {
      const session = await response.json();
      // Navigate to the new session
      window.location.href = `/sessions/${session.id}`;
    }
  }

  onMount(loadSessions);
</script>

<main class="p-10 space-y-6 max-w-2xl mx-auto">
  <div class="flex items-center justify-between">
    <h1 class="h1">Harvest Hound</h1>
    <a href="/settings" class="btn preset-outlined-surface-500">Settings</a>
  </div>

  <p class="text-lg text-surface-600-400">Meal Planning for CSA Deliveries</p>

  <!-- Create Session -->
  <div class="card preset-outlined-surface-500 p-6 space-y-4">
    <h2 class="h3">New Planning Session</h2>
    <form
      onsubmit={(e) => {
        e.preventDefault();
        createSession();
      }}
      class="space-y-3"
    >
      <input
        type="text"
        bind:value={newSessionName}
        placeholder={getDefaultSessionName()}
        class="input w-full"
      />
      <button type="submit" class="btn preset-filled-primary-500">
        Create Session
      </button>
    </form>
  </div>

  <!-- Session List -->
  {#if loading}
    <p class="text-surface-600-400">Loading sessions...</p>
  {:else if sessions.length > 0}
    <div class="card preset-outlined-surface-500 p-6 space-y-4">
      <h2 class="h3">Recent Sessions</h2>
      <ul class="space-y-2">
        {#each sessions as session}
          <li>
            <a
              href="/sessions/{session.id}"
              class="block p-3 rounded hover:bg-surface-100-900 transition-colors"
            >
              <span class="font-medium">{session.name || "Untitled Session"}</span>
              <span class="text-sm text-surface-600-400 ml-2">
                {new Date(session.created_at).toLocaleDateString()}
              </span>
            </a>
          </li>
        {/each}
      </ul>
    </div>
  {/if}

  <!-- Quick Links -->
  <div class="grid grid-cols-2 gap-4">
    <a
      href="/inventory"
      class="card preset-outlined-surface-500 p-4 hover:bg-surface-100-900 transition-colors"
    >
      <h3 class="font-medium">Inventory</h3>
      <p class="text-sm text-surface-600-400">Manage ingredients</p>
    </a>
    <a
      href="/settings"
      class="card preset-outlined-surface-500 p-4 hover:bg-surface-100-900 transition-colors"
    >
      <h3 class="font-medium">Settings</h3>
      <p class="text-sm text-surface-600-400">Configure profile</p>
    </a>
  </div>
</main>
