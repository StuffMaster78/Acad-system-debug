<script setup lang="ts">
import { computed } from "vue";
import {
  Briefcase,
  Headphones,
  ShieldCheck,
  FileEdit,
} from "@lucide/vue";
import { useAuthStore } from "@/stores/auth";
import { useWebsitesStore } from "@/stores/websites";
import type { UserRole } from "@/types/roles";

const props = defineProps<{ role: UserRole }>();

const auth  = useAuthStore();
const sites = useWebsitesStore();

const STAFF_ROLES: UserRole[] = ["admin", "superadmin", "editor", "support"];
const shouldShow = computed(() => STAFF_ROLES.includes(props.role));

const icon = computed(() => {
  if (props.role === "superadmin") return ShieldCheck;
  if (props.role === "editor")     return FileEdit;
  if (props.role === "support")    return Headphones;
  return Briefcase;
});

const label = computed(() => {
  if (props.role === "superadmin") return "Platform";
  if (props.role === "editor")     return "Editor desk";
  if (props.role === "support")    return "Support desk";
  // admin: try to show the active website name
  const website = sites.list[0];
  return website?.name ?? "Admin console";
});

const colorClass = computed(() => {
  if (props.role === "superadmin") return "border-violet-200 bg-violet-50 text-violet-800";
  if (props.role === "editor")     return "border-sky-200   bg-sky-50   text-sky-800";
  if (props.role === "support")    return "border-amber-200 bg-amber-50 text-amber-800";
  return                                  "border-slate-200 bg-slate-50 text-slate-700";
});

const iconColor = computed(() => {
  if (props.role === "superadmin") return "text-violet-500";
  if (props.role === "editor")     return "text-sky-500";
  if (props.role === "support")    return "text-amber-500";
  return                                  "text-slate-400";
});
</script>

<template>
  <div
    v-if="shouldShow"
    class="hidden min-h-8 items-center gap-1.5 whitespace-nowrap rounded-full border px-4 text-[13px] font-semibold md:inline-flex"
    :class="colorClass"
  >
    <component :is="icon" class="h-3.5 w-3.5 shrink-0" :class="iconColor" />
    <span>{{ label }}</span>
  </div>
</template>
