<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";

  interface Session {
    id: string;
    name: string;
    created_at: string;
  }

  interface Criterion {
    id: string;
    description: string;
    slots: number;
    created_at: string;
  }

  let session: Session | null = $state(null);
  let criteria: Criterion[] = $state([]);
  let loading = $state(true);
  let error = $state("");

  // Form state
  let newDescription = $state("");
  let newSlots = $state(1);
  let submitting = $state(false);

  // Generation state
  let generating = $state(false);
  let generationProgress = $state("");
  let generationError = $state("");

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

  async function loadCriteria() {
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}/criteria`);
    if (response.ok) {
      criteria = await response.json();
    }
  }

  async function addCriterion() {
    if (!newDescription.trim() || submitting) return;

    submitting = true;
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}/criteria`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        description: newDescription.trim(),
        slots: newSlots,
      }),
    });

    if (response.ok) {
      newDescription = "";
      newSlots = 1;
      await loadCriteria();
    }
    submitting = false;
  }

  async function deleteCriterion(criterionId: string) {
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}/criteria/${criterionId}`, {
      method: "DELETE",
    });
    if (response.ok) {
      await loadCriteria();
    }
  }

  async function generatePitches() {
    if (generating) return;

    generating = true;
    generationProgress = "Starting generation...";
    generationError = "";

    const id = $page.params.id;
    const eventSource = new EventSource(`/api/sessions/${id}/generate-pitches`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.error) {
        generationError = data.message;
        generationProgress = "";
        generating = false;
        eventSource.close();
      } else if (data.complete) {
        generationProgress = "Generation complete!";
        generating = false;
        eventSource.close();
        // Reload criteria to show pitches (Phase 6 will add pitch display)
        setTimeout(() => {
          generationProgress = "";
        }, 2000);
      } else if (data.progress) {
        generationProgress = `Generating for "${data.criterion_description}" (${data.criterion_index} of ${data.total_criteria}) - ${data.generating_count} pitches...`;
      } else if (data.pitch) {
        generationProgress = `Generated pitch ${data.pitch_index} of ${data.total_for_criterion} for this criterion`;
      }
    };

    eventSource.onerror = () => {
      generationError = "Connection lost. Please try again.";
      generationProgress = "";
      generating = false;
      eventSource.close();
    };
  }

  onMount(async () => {
    await loadSession();
    if (!error) {
      await loadCriteria();
    }
  });
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

    <!-- Meal Criteria -->
    <div class="card preset-outlined-surface-500 p-6 space-y-4">
      <h2 class="h3">Meal Criteria</h2>

      <!-- Add Criterion Form -->
      <form
        onsubmit={(e) => {
          e.preventDefault();
          addCriterion();
        }}
        class="space-y-3"
      >
        <div class="flex gap-3">
          <input
            type="text"
            bind:value={newDescription}
            placeholder="e.g., Quick weeknight meals"
            class="input flex-1"
            disabled={submitting}
          />
          <div class="flex items-center gap-2">
            <label for="slots" class="text-sm text-surface-600-400">Slots:</label>
            <input
              id="slots"
              type="number"
              bind:value={newSlots}
              min="1"
              max="7"
              class="input w-16 text-center"
              disabled={submitting}
            />
          </div>
        </div>
        <button
          type="submit"
          class="btn preset-filled-primary-500"
          disabled={!newDescription.trim() || submitting}
        >
          Add Criterion
        </button>
      </form>

      <!-- Criteria List -->
      {#if criteria.length > 0}
        <ul class="space-y-2 mt-4">
          {#each criteria as criterion}
            <li
              class="flex items-center justify-between p-3 rounded bg-surface-100-900"
            >
              <div>
                <span class="font-medium">{criterion.description}</span>
                <span class="text-sm text-surface-600-400 ml-2">
                  ({criterion.slots}
                  {criterion.slots === 1 ? "slot" : "slots"})
                </span>
              </div>
              <button
                onclick={() => deleteCriterion(criterion.id)}
                class="btn btn-sm preset-outlined-error-500"
                aria-label="Delete criterion"
              >
                Delete
              </button>
            </li>
          {/each}
        </ul>
      {:else}
        <p class="text-surface-600-400 text-sm">
          No criteria yet. Add criteria to define your meal planning constraints.
        </p>
      {/if}
    </div>

    <!-- Recipe Pitch Generation -->
    <div class="card preset-outlined-surface-500 p-6 space-y-4">
      <h2 class="h3">Recipe Pitches</h2>
      {#if criteria.length === 0}
        <p class="text-surface-600-400">
          Add at least one criterion to generate recipe pitches.
        </p>
      {:else}
        <p class="text-surface-600-400">
          Ready to generate pitches for {criteria.length}
          {criteria.length === 1 ? "criterion" : "criteria"}.
        </p>
        <button
          class="btn preset-filled-secondary-500"
          disabled={generating}
          onclick={generatePitches}
        >
          {generating ? "Generating..." : "Generate Pitches"}
        </button>

        {#if generationProgress}
          <div class="card preset-outlined-primary-500 p-4">
            <p class="text-sm">{generationProgress}</p>
          </div>
        {/if}

        {#if generationError}
          <div class="card preset-outlined-error-500 p-4">
            <p class="text-sm text-error-500">{generationError}</p>
          </div>
        {/if}

        <!-- Phase 6 will add pitch display here -->
      {/if}
    </div>
  {/if}
</main>
