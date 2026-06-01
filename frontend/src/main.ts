import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import { router } from "./router";
import "./styles/main.css";
import { usePortalContextStore } from "@/stores/portalContext";
import { useWebsitesStore } from "@/stores/websites";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();
  app.use(pinia);

  // Resolve portal surface before the router starts so the navigation guard
  // can make synchronous surface decisions on the first navigation.
  const portalStore = usePortalContextStore();
  await portalStore.init();

  // Pre-load website list so nameById() resolves everywhere without extra fetches.
  useWebsitesStore().ensure().catch(() => undefined);

  app.use(router).mount("#app");
}

bootstrap();
