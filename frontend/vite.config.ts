/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Phase 1: default Vite + React + TS setup. The dev server proxies /api
// calls to the FastAPI backend so the browser never needs to know the
// backend's real port — this avoids CORS friction in local development
// and mirrors how a reverse proxy (nginx) will route in Docker/production.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    globals: true,
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/health": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
