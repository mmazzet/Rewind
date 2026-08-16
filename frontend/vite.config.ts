import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  const usePolling = env.VITE_USE_POLLING === "1";

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: "0.0.0.0",
      allowedHosts: true,
      watch: {
        usePolling,
        interval: 1000,
      },
      proxy: {
        "/api": {
          target: "http://backend:8000",
          changeOrigin: true,
        },
      },
    },
  };
});
