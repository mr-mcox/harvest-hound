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

  interface PitchIngredient {
    name: string;
    quantity: number;
    unit: string;
  }

  interface Pitch {
    id: string;
    criterion_id: string;
    name: string;
    blurb: string;
    why_make_this: string;
    inventory_ingredients: PitchIngredient[];
    active_time_minutes: number;
    created_at: string;
  }

  let session: Session | null = $state(null);
  let criteria: Criterion[] = $state([]);
  let pitches: Pitch[] = $state([]);
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

  // Derived: pitches grouped by criterion
  let pitchesByCriterion = $derived(() => {
    const grouped: Record<string, Pitch[]> = {};
    for (const pitch of pitches) {
      if (!grouped[pitch.criterion_id]) {
        grouped[pitch.criterion_id] = [];
      }
      grouped[pitch.criterion_id].push(pitch);
    }
    return grouped;
  });

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

  async function loadPitches() {
    const id = $page.params.id;
    const response = await fetch(`/api/sessions/${id}/pitches`);
    if (response.ok) {
      pitches = await response.json();
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
        setTimeout(() => {
          generationProgress = "";
        }, 2000);
      } else if (data.progress) {
        generationProgress = `Generating for "${data.criterion_description}" (${data.criterion_index} of ${data.total_criteria}) - ${data.generating_count} pitches...`;
      } else if (data.pitch) {
        // Accumulate pitch in real-time
        const newPitch: Pitch = {
          id: data.data.id,
          criterion_id: data.criterion_id,
          name: data.data.name,
          blurb: data.data.blurb,
          why_make_this: data.data.why_make_this,
          inventory_ingredients: data.data.inventory_ingredients,
          active_time_minutes: data.data.active_time_minutes,
          created_at: new Date().toISOString(),
        };
        pitches = [...pitches, newPitch];
        generationProgress = `Generated "${newPitch.name}" (${data.pitch_index} of ${data.total_for_criterion})`;
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
      await loadPitches();
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

        <!-- Pitches grouped by criterion -->
        {#each criteria as criterion}
          {@const criterionPitches = pitchesByCriterion()[criterion.id] || []}
          <div class="space-y-3 mt-6">
            <h3 class="h4 text-surface-700-300">
              {criterion.description}
              <span class="text-sm font-normal text-surface-500">
                ({criterionPitches.length} / {criterion.slots * 3} pitches)
              </span>
            </h3>

            {#if criterionPitches.length === 0}
              <p class="text-sm text-surface-500 italic">No pitches yet</p>
            {:else}
              <div class="grid gap-3">
                {#each criterionPitches as pitch}
                  <div class="card preset-outlined-surface-500 p-4 space-y-2">
                    <div class="flex items-start justify-between">
                      <h4 class="font-semibold text-lg">{pitch.name}</h4>
                      <span class="text-sm text-surface-500">
                        {pitch.active_time_minutes} min
                      </span>
                    </div>
                    <p class="text-surface-600-400 italic">{pitch.blurb}</p>
                    <p class="text-sm text-surface-600-400">{pitch.why_make_this}</p>
                    {#if pitch.inventory_ingredients.length > 0}
                      <div class="text-sm">
                        <span class="font-medium">Uses:</span>
                        {pitch.inventory_ingredients
                          .map((i) => `${i.quantity} ${i.unit} ${i.name}`)
                          .join(", ")}
                      </div>
                    {/if}
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      {/if}
    </div>
  {/if}
</main>
