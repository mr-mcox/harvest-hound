<script lang="ts">
    let message = $state("Click the button to say hello!");

    function sayHello() {
        message = "Hello from Harvest Hound!";
    }
</script>

<main class="p-10 space-y-6">
    <h1 class="h1">Harvest Hound</h1>
    <p class="text-lg">{message}</p>
    <button
        type="button"
        class="btn preset-filled-primary-500"
        onclick={sayHello}
    >
        Say Hello
    </button>
</main>
