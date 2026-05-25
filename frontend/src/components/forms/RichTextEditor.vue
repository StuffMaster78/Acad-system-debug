<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import { Bold, Heading2, Italic, Link, List } from "@lucide/vue";

const props = defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: string];
}>();

const editor = ref<HTMLElement | null>(null);

function setEditorHtml(value: string) {
  if (editor.value && editor.value.innerHTML !== value) {
    editor.value.innerHTML = value;
  }
}

watch(
  () => props.modelValue,
  (value) => {
    setEditorHtml(value);
  },
  { immediate: true },
);

onMounted(() => {
  setEditorHtml(props.modelValue);
});

function sync() {
  emit("update:modelValue", editor.value?.innerHTML ?? "");
}

async function command(name: string, value?: string) {
  editor.value?.focus();
  document.execCommand(name, false, value);
  await nextTick();
  sync();
}

function createLink() {
  const url = window.prompt("Link URL");
  if (url) command("createLink", url);
}
</script>

<template>
  <div class="rounded-md border border-slate-200 bg-white">
    <div class="flex flex-wrap gap-1 border-b border-slate-200 bg-slate-50 p-2">
      <button
        class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white"
        type="button"
        title="Bold"
        @click="command('bold')"
      >
        <Bold class="h-4 w-4" />
      </button>
      <button
        class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white"
        type="button"
        title="Italic"
        @click="command('italic')"
      >
        <Italic class="h-4 w-4" />
      </button>
      <button
        class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white"
        type="button"
        title="Heading"
        @click="command('formatBlock', 'h2')"
      >
        <Heading2 class="h-4 w-4" />
      </button>
      <button
        class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white"
        type="button"
        title="Bullet list"
        @click="command('insertUnorderedList')"
      >
        <List class="h-4 w-4" />
      </button>
      <button
        class="focus-ring inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-200 bg-white"
        type="button"
        title="Link"
        @click="createLink"
      >
        <Link class="h-4 w-4" />
      </button>
    </div>
    <div
      ref="editor"
      class="prose prose-sm min-h-36 max-w-none px-3 py-2 text-sm leading-6 outline-none"
      contenteditable="true"
      @input="sync"
      @blur="sync"
    />
  </div>
</template>
