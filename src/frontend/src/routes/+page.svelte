<script lang="ts">
  interface Dish {
    name: string;
    description: string;
  }

  let ingredient = $state("");
  let dishes = $state<Dish[]>([]);
  let loading = $state(false);
  let streaming = $state(false);
  let error = $state<string | null>(null);
  let eventSource: EventSource | null = null;

  async function getDishes() {
    if (!ingredient.trim()) {
      error = "Please enter an ingredient";
      return;
    }

    loading = true;
    error = null;
    dishes = [];

    try {
      const response = await fetch(
        `/api/dishes?ingredient=${encodeURIComponent(ingredient)}`
      );
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      dishes = await response.json();
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to fetch dishes";
    } finally {
      loading = false;
    }
  }

  function streamDishes() {
    if (!ingredient.trim()) {
      error = "Please enter an ingredient";
      return;
    }

    if (eventSource) {
      eventSource.close();
    }

    streaming = true;
    error = null;
    dishes = [];

    eventSource = new EventSource(
      `/api/dishes/stream?ingredient=${encodeURIComponent(ingredient)}`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.complete) {
        eventSource?.close();
        eventSource = null;
        streaming = false;
      } else if (data.error) {
        error = data.message;
        eventSource?.close();
        eventSource = null;
        streaming = false;
      } else {
        dishes = [...dishes, data];
      }
    };

    eventSource.onerror = () => {
      error = "Connection lost";
      eventSource?.close();
      eventSource = null;
      streaming = false;
    };
  }
</script>

<main class="p-10 space-y-6 max-w-2xl mx-auto">
  <h1 class="h1">Harvest Hound</h1>
  <p class="text-lg text-surface-600-400">
    Enter an ingredient to discover creative dish ideas.
  </p>

  <div class="flex gap-4">
    <input
      type="text"
      class="input px-4 py-2 flex-1"
      placeholder="e.g., carrot, potato, kale..."
      bind:value={ingredient}
      onkeydown={(e) => e.key === "Enter" && streamDishes()}
    />
    <button
      type="button"
      class="btn preset-filled-primary-500"
      onclick={getDishes}
      disabled={loading || streaming}
    >
      {loading ? "Loading..." : "Get All"}
    </button>
    <button
      type="button"
      class="btn preset-filled-secondary-500"
      onclick={streamDishes}
      disabled={loading || streaming}
    >
      {streaming ? "Streaming..." : "Stream"}
    </button>
  </div>

  {#if error}
    <div class="card preset-outlined-error-500 p-4">
      <p>{error}</p>
    </div>
  {/if}

  {#if dishes.length > 0}
    <div class="space-y-4">
      <h2 class="h3">Dish Ideas for "{ingredient}"</h2>
      <div class="grid gap-4">
        {#each dishes as dish}
          <div class="card preset-outlined-surface-500 p-4 space-y-2">
            <h3 class="h4">{dish.name}</h3>
            <p class="text-surface-600-400">{dish.description}</p>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</main>
