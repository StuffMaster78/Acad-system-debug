<script setup lang="ts">
import BaseModal from "@/components/ui/BaseModal.vue";

withDefaults(defineProps<{
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  tone?: "danger" | "warning" | "neutral";
}>(), {
  confirmLabel: "Confirm",
  cancelLabel: "Cancel",
  tone: "neutral",
});

const emit = defineEmits<{
  close: [];
  confirm: [];
}>();

const buttonClasses = {
  danger: "bg-rose-700 text-white hover:bg-rose-800",
  warning: "bg-amber-600 text-white hover:bg-amber-700",
  neutral: "bg-ink text-white hover:bg-graphite",
};
</script>

<template>
  <BaseModal
    :open="open"
    :title="title"
    @close="emit('close')"
  >
    <p class="text-sm leading-6 text-graphite">{{ message }}</p>

    <template #footer>
      <div class="flex justify-end gap-2">
        <button
          class="focus-ring inline-flex h-10 items-center justify-center rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
          type="button"
          @click="emit('close')"
        >
          {{ cancelLabel }}
        </button>
        <button
          class="focus-ring inline-flex h-10 items-center justify-center rounded-md px-4 text-sm font-semibold"
          :class="buttonClasses[tone]"
          type="button"
          @click="emit('confirm')"
        >
          {{ confirmLabel }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>
