<script setup lang="ts">
import { computed } from "vue";
import { Globe, Lock, Building2 } from "@lucide/vue";
import type { ConfigDefinition } from "@/types/config";

const props = defineProps<{
  definition: ConfigDefinition;
  modelValue: unknown;
  savedValue: unknown;
  lastChangedBy: string | null;
  lastChangedAt: string | null;
  isOverridden: boolean;
  readonly: boolean;
  websiteMode: boolean; // true when a specific website is selected
}>();

const emit = defineEmits<{
  "update:modelValue": [value: unknown];
}>();

const isDirty = computed(() => props.modelValue !== props.savedValue);

const scopeColors: Record<string, string> = {
  superadmin: "bg-rose-50 text-rose-700 border-rose-200",
  admin: "bg-amber-50 text-amber-700 border-amber-200",
  editor: "bg-sky-50 text-sky-700 border-sky-200",
  support: "bg-slate-100 text-graphite border-slate-200",
};

const scopeLabel: Record<string, string> = {
  superadmin: "Superadmin",
  admin: "Admin",
  editor: "Editor",
  support: "Support",
};

function relativeTime(iso: string | null) {
  if (!iso) return null;
  const diff = Date.now() - new Date(iso).getTime();
  const min = Math.floor(diff / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h ago`;
  return `${Math.floor(hr / 24)}d ago`;
}

function handleInput(e: Event) {
  const target = e.target as HTMLInputElement;
  const def = props.definition;
  if (def.dataType === "boolean") {
    emit("update:modelValue", target.checked);
  } else if (def.dataType === "number" || def.dataType === "percentage" || def.dataType === "currency") {
    emit("update:modelValue", target.value === "" ? null : Number(target.value));
  } else {
    emit("update:modelValue", target.value);
  }
}

function handleSelect(e: Event) {
  emit("update:modelValue", (e.target as HTMLSelectElement).value);
}
</script>

<template>
  <div
    class="group rounded-lg border p-4 transition-colors"
    :class="[
      isDirty ? 'border-amber-200 bg-amber-50/40' : 'border-slate-100 bg-white hover:border-slate-200',
      definition.isSensitive ? 'border-l-2 border-l-rose-400' : '',
    ]"
  >
    <div class="flex items-start justify-between gap-4">
      <!-- Label + description -->
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-sm font-medium text-ink">{{ definition.label }}</span>

          <!-- Dirty indicator -->
          <span v-if="isDirty" class="size-1.5 rounded-full bg-amber-500" title="Unsaved change" />

          <!-- Scope badge -->
          <span
            class="rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
            :class="scopeColors[definition.requiredScope]"
          >{{ scopeLabel[definition.requiredScope] }}</span>

          <!-- Sensitive badge -->
          <span v-if="definition.isSensitive" class="flex items-center gap-0.5 rounded border border-rose-200 bg-rose-50 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-rose-700">
            <Lock class="size-2.5" /> Sensitive
          </span>

          <!-- Website override indicator -->
          <span v-if="websiteMode" class="flex items-center gap-0.5 rounded border px-1.5 py-0.5 text-[10px] font-medium"
            :class="isOverridden ? 'border-berry/30 bg-berry/5 text-berry' : 'border-slate-200 text-graphite'">
            <component :is="isOverridden ? Building2 : Globe" class="size-2.5" />
            {{ isOverridden ? "Website override" : "Using global" }}
          </span>
        </div>
        <p class="mt-0.5 text-xs text-graphite">{{ definition.description }}</p>
      </div>

      <!-- Input -->
      <div class="w-52 shrink-0">
        <!-- Boolean toggle -->
        <template v-if="definition.dataType === 'boolean'">
          <label class="flex cursor-pointer items-center gap-2" :class="readonly ? 'pointer-events-none opacity-60' : ''">
            <div class="relative">
              <input
                type="checkbox"
                class="sr-only"
                :checked="Boolean(modelValue)"
                :disabled="readonly"
                @change="handleInput"
              />
              <div
                class="h-5 w-9 rounded-full transition-colors"
                :class="modelValue ? 'bg-berry' : 'bg-slate-200'"
              />
              <div
                class="absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform"
                :class="modelValue ? 'translate-x-4' : 'translate-x-0'"
              />
            </div>
            <span class="text-sm" :class="modelValue ? 'text-berry font-medium' : 'text-graphite'">
              {{ modelValue ? "Enabled" : "Disabled" }}
            </span>
          </label>
        </template>

        <!-- Select -->
        <template v-else-if="definition.dataType === 'select'">
          <select
            :value="String(modelValue ?? '')"
            :disabled="readonly"
            class="w-full rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm focus-ring disabled:cursor-not-allowed disabled:opacity-60"
            @change="handleSelect"
          >
            <option v-for="opt in definition.options" :key="String(opt.value)" :value="String(opt.value)">
              {{ opt.label }}
            </option>
          </select>
        </template>

        <!-- Textarea -->
        <template v-else-if="definition.dataType === 'textarea'">
          <textarea
            :value="String(modelValue ?? '')"
            :disabled="readonly"
            rows="3"
            class="w-full resize-y rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring disabled:cursor-not-allowed disabled:opacity-60"
            @input="handleInput"
          />
        </template>

        <!-- Percentage -->
        <template v-else-if="definition.dataType === 'percentage'">
          <div class="flex items-center gap-1">
            <input
              type="number"
              min="0"
              max="1000"
              :value="modelValue"
              :disabled="readonly"
              class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring disabled:cursor-not-allowed disabled:opacity-60"
              @input="handleInput"
            />
            <span class="text-sm text-graphite">%</span>
          </div>
        </template>

        <!-- Currency -->
        <template v-else-if="definition.dataType === 'currency'">
          <div class="flex items-center gap-1">
            <span class="text-sm text-graphite">$</span>
            <input
              type="number"
              min="0"
              step="0.01"
              :value="modelValue"
              :disabled="readonly"
              class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring disabled:cursor-not-allowed disabled:opacity-60"
              @input="handleInput"
            />
          </div>
        </template>

        <!-- Number / Text fallback -->
        <template v-else>
          <input
            :type="definition.dataType === 'number' ? 'number' : 'text'"
            :value="modelValue"
            :disabled="readonly"
            class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring disabled:cursor-not-allowed disabled:opacity-60"
            @input="handleInput"
          />
        </template>
      </div>
    </div>

    <!-- Footer: default + last changed -->
    <div class="mt-2 flex items-center justify-between text-[11px] text-graphite">
      <span>Default: <code class="rounded bg-slate-100 px-1 py-0.5 text-[10px]">{{ String(definition.defaultValue) }}</code></span>
      <span v-if="lastChangedBy" class="flex items-center gap-1">
        {{ lastChangedBy }}
        <span v-if="lastChangedAt">· {{ relativeTime(lastChangedAt) }}</span>
      </span>
    </div>
  </div>
</template>
