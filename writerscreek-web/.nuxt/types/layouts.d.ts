import type { ComputedRef, MaybeRef } from 'vue'
export type LayoutKey = "default"
declare module "../../node_modules/.pnpm/nuxt@3.16.2_@parcel+watcher@2.5.6_cac@6.7.14_db0@0.3.4_ioredis@5.11.1_lightningcss@1.32_eb869fa7e06903a95f78d3b0291379e5/node_modules/nuxt/dist/pages/runtime/composables" {
  interface PageMeta {
    layout?: MaybeRef<LayoutKey | false> | ComputedRef<LayoutKey | false>
  }
}