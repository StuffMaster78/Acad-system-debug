<template>
  <div class="rich-editor rounded-lg border border-slate-200 bg-white focus-within:border-berry focus-within:ring-1 focus-within:ring-berry/30">
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-0.5 border-b border-slate-200 px-2 py-1.5">
      <!-- Text style -->
      <ToolbarGroup>
        <ToolBtn title="Bold (⌘B)" :active="editor?.isActive('bold')" @click="editor?.chain().focus().toggleBold().run()">
          <Bold class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Italic (⌘I)" :active="editor?.isActive('italic')" @click="editor?.chain().focus().toggleItalic().run()">
          <Italic class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Underline (⌘U)" :active="editor?.isActive('underline')" @click="editor?.chain().focus().toggleUnderline().run()">
          <Underline class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Strikethrough" :active="editor?.isActive('strike')" @click="editor?.chain().focus().toggleStrike().run()">
          <Strikethrough class="size-3.5" />
        </ToolBtn>
      </ToolbarGroup>

      <div class="mx-1 h-5 w-px bg-slate-200" />

      <!-- Headings -->
      <ToolbarGroup>
        <ToolBtn title="Heading 2" :active="editor?.isActive('heading', { level: 2 })" @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()">
          <Heading2 class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Heading 3" :active="editor?.isActive('heading', { level: 3 })" @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()">
          <Heading3 class="size-3.5" />
        </ToolBtn>
      </ToolbarGroup>

      <div class="mx-1 h-5 w-px bg-slate-200" />

      <!-- Lists -->
      <ToolbarGroup>
        <ToolBtn title="Bullet list" :active="editor?.isActive('bulletList')" @click="editor?.chain().focus().toggleBulletList().run()">
          <List class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Numbered list" :active="editor?.isActive('orderedList')" @click="editor?.chain().focus().toggleOrderedList().run()">
          <ListOrdered class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Blockquote" :active="editor?.isActive('blockquote')" @click="editor?.chain().focus().toggleBlockquote().run()">
          <Quote class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Code block" :active="editor?.isActive('codeBlock')" @click="editor?.chain().focus().toggleCodeBlock().run()">
          <Code2 class="size-3.5" />
        </ToolBtn>
      </ToolbarGroup>

      <div class="mx-1 h-5 w-px bg-slate-200" />

      <!-- Alignment -->
      <ToolbarGroup>
        <ToolBtn title="Align left" :active="editor?.isActive({ textAlign: 'left' })" @click="editor?.chain().focus().setTextAlign('left').run()">
          <AlignLeft class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Align center" :active="editor?.isActive({ textAlign: 'center' })" @click="editor?.chain().focus().setTextAlign('center').run()">
          <AlignCenter class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Align right" :active="editor?.isActive({ textAlign: 'right' })" @click="editor?.chain().focus().setTextAlign('right').run()">
          <AlignRight class="size-3.5" />
        </ToolBtn>
      </ToolbarGroup>

      <div class="mx-1 h-5 w-px bg-slate-200" />

      <!-- Link + misc -->
      <ToolbarGroup>
        <ToolBtn title="Insert link" :active="editor?.isActive('link')" @click="toggleLink">
          <Link2 class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Remove link" :disabled="!editor?.isActive('link')" @click="editor?.chain().focus().unsetLink().run()">
          <Link2Off class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Horizontal rule" @click="editor?.chain().focus().setHorizontalRule().run()">
          <Minus class="size-3.5" />
        </ToolBtn>
      </ToolbarGroup>

      <div class="mx-1 h-5 w-px bg-slate-200" />

      <!-- Undo / redo -->
      <ToolbarGroup>
        <ToolBtn title="Undo (⌘Z)" :disabled="!editor?.can().undo()" @click="editor?.chain().focus().undo().run()">
          <Undo2 class="size-3.5" />
        </ToolBtn>
        <ToolBtn title="Redo (⌘⇧Z)" :disabled="!editor?.can().redo()" @click="editor?.chain().focus().redo().run()">
          <Redo2 class="size-3.5" />
        </ToolBtn>
      </ToolbarGroup>

      <div class="ml-auto text-xs text-slate-400">
        {{ wordCount }} word{{ wordCount !== 1 ? 's' : '' }}
      </div>
    </div>

    <!-- Link input dialog -->
    <div v-if="showLinkInput" class="flex items-center gap-2 border-b border-slate-200 bg-slate-50 px-3 py-2">
      <input
        ref="linkInputRef"
        v-model="linkUrl"
        class="focus-ring min-w-0 flex-1 rounded border border-slate-200 px-2 py-1 text-sm"
        type="url"
        placeholder="https://example.com"
        @keydown.enter="applyLink"
        @keydown.escape="showLinkInput = false"
      />
      <button class="rounded bg-berry px-2 py-1 text-xs font-semibold text-white hover:bg-rose-700" @click="applyLink">Apply</button>
      <button class="rounded border border-slate-200 px-2 py-1 text-xs text-graphite hover:bg-slate-100" @click="showLinkInput = false">Cancel</button>
    </div>

    <!-- Editor content -->
    <EditorContent
      :editor="editor"
      class="prose prose-slate max-w-none focus:outline-none"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import StarterKit from "@tiptap/starter-kit";
import UnderlineExt from "@tiptap/extension-underline";
import LinkExt from "@tiptap/extension-link";
import PlaceholderExt from "@tiptap/extension-placeholder";
import TextAlignExt from "@tiptap/extension-text-align";
import {
  AlignCenter, AlignLeft, AlignRight,
  Bold, Code2, Heading2, Heading3,
  Italic, Link2, Link2Off, List, ListOrdered,
  Minus, Quote, Redo2, Strikethrough, Underline, Undo2,
} from "@lucide/vue";

// Sub-components defined inline to keep this file self-contained
import { defineComponent, h } from "vue";

const ToolbarGroup = defineComponent({
  render() { return h("div", { class: "flex items-center gap-0.5" }, this.$slots.default?.()); },
});

const ToolBtn = defineComponent({
  props: { active: Boolean, disabled: Boolean, title: String },
  emits: ["click"],
  render() {
    return h("button", {
      type: "button",
      title: this.title,
      disabled: this.disabled,
      onClick: () => this.$emit("click"),
      class: [
        "flex size-7 items-center justify-center rounded transition-colors",
        this.active
          ? "bg-berry/10 text-berry"
          : "text-graphite hover:bg-slate-100 hover:text-ink",
        this.disabled ? "opacity-40 cursor-not-allowed" : "cursor-pointer",
      ].filter(Boolean).join(" "),
    }, this.$slots.default?.());
  },
});

// Props / emits
const props = withDefaults(defineProps<{
  modelValue: string;
  placeholder?: string;
  minHeight?: string;
}>(), {
  placeholder: "Start writing…",
  minHeight: "300px",
});

const emit = defineEmits<{ "update:modelValue": [value: string] }>();

// Link dialog
const showLinkInput = ref(false);
const linkUrl = ref("");
const linkInputRef = ref<HTMLInputElement | null>(null);

function toggleLink() {
  if (editor.value?.isActive("link")) {
    editor.value.chain().focus().unsetLink().run();
  } else {
    linkUrl.value = "";
    showLinkInput.value = true;
    nextTick(() => linkInputRef.value?.focus());
  }
}

function applyLink() {
  if (linkUrl.value) {
    editor.value?.chain().focus().setLink({ href: linkUrl.value, target: "_blank" }).run();
  }
  showLinkInput.value = false;
}

// Editor
const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    UnderlineExt,
    LinkExt.configure({ openOnClick: false, HTMLAttributes: { rel: "noopener noreferrer" } }),
    PlaceholderExt.configure({ placeholder: props.placeholder }),
    TextAlignExt.configure({ types: ["heading", "paragraph"] }),
  ],
  editorProps: {
    attributes: {
      class: "outline-none px-4 py-3",
      style: `min-height: ${props.minHeight}`,
    },
  },
  onUpdate({ editor }) {
    emit("update:modelValue", editor.getHTML());
  },
});

// Sync external changes (e.g. loading saved content)
watch(
  () => props.modelValue,
  (val) => {
    if (editor.value && editor.value.getHTML() !== val) {
      editor.value.commands.setContent(val, false);
    }
  },
);

const wordCount = computed(() => {
  const text = editor.value?.getText() ?? "";
  return text.trim() ? text.trim().split(/\s+/).length : 0;
});

onBeforeUnmount(() => editor.value?.destroy());
</script>

<style>
/* TipTap placeholder */
.tiptap p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  float: left;
  color: #94a3b8;
  pointer-events: none;
  height: 0;
}

/* Prose styles scoped to editor content */
.rich-editor .ProseMirror h2 { @apply mt-6 text-xl font-semibold text-gray-900; }
.rich-editor .ProseMirror h3 { @apply mt-5 text-base font-semibold text-gray-900; }
.rich-editor .ProseMirror p  { @apply leading-7 text-gray-700; }
.rich-editor .ProseMirror ul { @apply my-3 list-disc space-y-1 pl-5 text-gray-700; }
.rich-editor .ProseMirror ol { @apply my-3 list-decimal space-y-1 pl-5 text-gray-700; }
.rich-editor .ProseMirror blockquote { @apply border-l-4 border-slate-200 pl-4 italic text-gray-500; }
.rich-editor .ProseMirror code { @apply rounded bg-slate-100 px-1 py-0.5 font-mono text-sm text-rose-600; }
.rich-editor .ProseMirror pre  { @apply my-4 rounded-lg bg-slate-900 p-4 text-sm text-white; }
.rich-editor .ProseMirror pre code { @apply bg-transparent text-white; }
.rich-editor .ProseMirror a { @apply text-rose-600 underline; }
.rich-editor .ProseMirror hr { @apply my-6 border-slate-200; }
</style>
