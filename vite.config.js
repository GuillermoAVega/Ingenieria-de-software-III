import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/clientes": "http://localhost:8000",
      "/productos": "http://localhost:8000",
      "/ventas": "http://localhost:8000",
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/frontend/setup.js"],
    include: ["tests/frontend/**/*.test.{js,jsx}"],
  },
});
