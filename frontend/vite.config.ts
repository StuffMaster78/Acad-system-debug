import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const BACKEND = process.env.VITE_BACKEND_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Django REST API + Wagtail headless API
      "/api/": { target: BACKEND, changeOrigin: true },
      // Custom CMS API
      "/cms-api/": { target: BACKEND, changeOrigin: true },
      // Wagtail admin UI (staff only)
      "/cms-admin/": { target: BACKEND, changeOrigin: true },
      // SEO pages API
      "/seo-pages/": { target: BACKEND, changeOrigin: true },
      // Django static files (admin CSS/JS, Wagtail UI assets)
      "/static/": { target: BACKEND, changeOrigin: true },
      // User-uploaded media
      "/media/": { target: BACKEND, changeOrigin: true },
      // Health endpoints
      "/health/": { target: BACKEND, changeOrigin: true },
      // Wagtail front-end page serving (CMS public pages)
      "/cms/": { target: BACKEND, changeOrigin: true },
    },
  },
});
