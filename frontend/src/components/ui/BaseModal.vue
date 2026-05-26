<script setup lang="ts">
import { X } from "@lucide/vue";

withDefaults(defineProps<{
  open: boolean;
  title: string;
  description?: string;
  size?: "md" | "lg" | "xl" | "full";
}>(), {
  description: "",
  size: "md",
});

const emit = defineEmits<{
  close: [];
}>();
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 px-4 py-6"
      role="presentation"
      @click.self="emit('close')"
    >
      <section
        class="max-h-[90vh] w-full overflow-y-auto rounded-md border border-slate-200 bg-white shadow-xl"
        :class="{
          'max-w-xl': size === 'md',
          'max-w-3xl': size === 'lg',
          'max-w-5xl': size === 'xl',
          'max-w-[min(1200px,calc(100vw-2rem))]': size === 'full',
        }"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
      >
        <header class="flex min-h-16 items-start justify-between gap-4 border-b border-slate-200 px-5 py-4">
          <div>
            <h2 class="text-lg font-semibold text-ink">{{ title }}</h2>
            <p v-if="description" class="mt-1 text-sm leading-6 text-graphite">{{ description }}</p>
          </div>
          <button
            class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200"
            type="button"
            title="Close"
            @click="emit('close')"
          >
            <X class="h-4 w-4" />
          </button>
        </header>
        <div class="p-5">
          <slot />
        </div>
        <footer v-if="$slots.footer" class="border-t border-slate-200 px-5 py-4">
          <slot name="footer" />
        </footer>
      </section>
    </div>
  </Teleport>
</template>
