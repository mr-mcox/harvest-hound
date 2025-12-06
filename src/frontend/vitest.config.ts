import path from "path";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { svelteTesting } from "@testing-library/svelte/vite";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [svelte(), svelteTesting()],
  resolve: {
    alias: {
      $lib: path.resolve(__dirname, "./src/lib"),
      "$app/navigation": path.resolve(__dirname, "./src/mocks/app-navigation.ts"),
    },
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.ts"],
    setupFiles: ["./src/setupTests.ts"],
  },
});
