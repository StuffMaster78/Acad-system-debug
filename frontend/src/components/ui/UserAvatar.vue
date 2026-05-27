<script setup lang="ts">
import { computed } from "vue";
import type { AuthUser } from "@/types/roles";

const props = withDefaults(
  defineProps<{
    user: Pick<AuthUser, "id" | "full_name" | "email" | "avatar_url"> | null | undefined;
    size?: "xs" | "sm" | "md" | "lg" | "xl";
  }>(),
  { size: "md" },
);

const PALETTE = [
  "bg-violet-500",
  "bg-blue-500",
  "bg-emerald-500",
  "bg-amber-500",
  "bg-rose-500",
  "bg-cyan-500",
  "bg-indigo-500",
  "bg-teal-500",
];

const initials = computed(() => {
  const name = props.user?.full_name?.trim();
  if (name) {
    const parts = name.split(/\s+/);
    return parts.length > 1
      ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
      : name.slice(0, 2).toUpperCase();
  }
  return (props.user?.email?.[0] ?? "?").toUpperCase();
});

const colorClass = computed(() => {
  const seed = props.user?.id ?? 0;
  return PALETTE[seed % PALETTE.length];
});

const sizeClasses = computed(() => {
  const map = {
    xs: "h-6 w-6 text-xs",
    sm: "h-8 w-8 text-xs",
    md: "h-10 w-10 text-sm",
    lg: "h-16 w-16 text-xl",
    xl: "h-24 w-24 text-3xl",
  };
  return map[props.size];
});
</script>

<template>
  <div
    class="shrink-0 overflow-hidden rounded-full"
    :class="sizeClasses"
    aria-hidden="true"
  >
    <img
      v-if="user?.avatar_url"
      :src="user.avatar_url"
      :alt="user?.full_name ?? user?.email ?? 'Avatar'"
      class="h-full w-full object-cover"
    />
    <div
      v-else
      class="flex h-full w-full items-center justify-center font-semibold text-white"
      :class="colorClass"
    >
      {{ initials }}
    </div>
  </div>
</template>
