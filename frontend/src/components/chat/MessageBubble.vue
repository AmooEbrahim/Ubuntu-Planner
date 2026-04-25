<template>
  <div class="flex gap-3" :class="alignClass">
    <div
      v-if="role !== 'user'"
      class="flex-shrink-0 h-9 w-9 rounded-xl text-white text-[11px] font-bold flex items-center justify-center select-none shadow-md"
      style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent))); box-shadow: 0 4px 12px rgba(168, 85, 247, 0.35);"
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
        <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"></path>
      </svg>
    </div>

    <div class="max-w-[78%] min-w-0 space-y-1.5">
      <div
        v-if="role === 'user'"
        class="rounded-2xl px-4 py-3 text-base leading-relaxed text-white shadow-md"
        :style="{
          background: 'linear-gradient(135deg, rgb(var(--accent)), rgb(var(--accent-hover)))',
          boxShadow: '0 6px 20px rgb(var(--accent) / 0.35)',
        }"
      >
        <div class="whitespace-pre-wrap">{{ content || '…' }}</div>
        <span v-if="streaming" class="inline-block w-1 h-4 bg-white/80 align-middle animate-pulse ml-0.5" />
      </div>

      <div
        v-else
        class="glass-card rounded-2xl px-4 py-3 text-base leading-relaxed text-fg"
      >
        <div class="markdown-body" v-html="renderedHtml" />
        <span v-if="streaming" class="inline-block w-1 h-4 bg-current align-middle animate-pulse ml-0.5" />
      </div>

      <div v-if="meta" class="text-[11px] text-subtle px-1">{{ meta }}</div>
    </div>

    <div
      v-if="role === 'user'"
      class="flex-shrink-0 h-9 w-9 rounded-xl text-white text-[11px] font-bold flex items-center justify-center select-none shadow-md"
      :style="{
        background: 'linear-gradient(135deg, rgb(var(--accent)), rgb(var(--accent-hover)))',
        boxShadow: '0 4px 12px rgb(var(--accent) / 0.35)',
      }"
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  typographer: false,
})

const props = defineProps({
  role: { type: String, required: true },
  content: { type: String, default: '' },
  streaming: { type: Boolean, default: false },
  meta: { type: String, default: '' },
})

const alignClass = computed(() => (props.role === 'user' ? 'justify-end' : 'justify-start'))

const renderedHtml = computed(() => {
  const text = props.content || (props.streaming ? '' : '…')
  if (!text) return ''
  return md.render(text)
})
</script>

<style scoped>
.markdown-body :deep(p) { margin: 0.35rem 0; }
.markdown-body :deep(p:first-child) { margin-top: 0; }
.markdown-body :deep(p:last-child) { margin-bottom: 0; }
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  font-weight: 700;
  margin: 0.6rem 0 0.3rem;
  line-height: 1.3;
}
.markdown-body :deep(h1) { font-size: 1.2rem; }
.markdown-body :deep(h2) { font-size: 1.1rem; }
.markdown-body :deep(h3) { font-size: 1.05rem; }
.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0.35rem 0 0.35rem 1.5rem;
  padding: 0;
}
.markdown-body :deep(li) { margin: 0.15rem 0; }
.markdown-body :deep(li > p) { margin: 0; }
.markdown-body :deep(strong) { font-weight: 600; }
.markdown-body :deep(em) { font-style: italic; }
.markdown-body :deep(a) {
  color: rgb(var(--accent));
  text-decoration: underline;
  text-underline-offset: 2px;
}
.markdown-body :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.9em;
  background: rgb(var(--fg-subtle) / 0.18);
  border-radius: 0.35rem;
  padding: 0.1rem 0.4rem;
}
.markdown-body :deep(pre) {
  background: rgb(15 23 42);
  color: rgb(229 231 235);
  border-radius: 0.7rem;
  padding: 0.85rem 1rem;
  overflow-x: auto;
  margin: 0.6rem 0;
  font-size: 0.875rem;
  line-height: 1.5;
}
.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
  font-size: inherit;
}
.markdown-body :deep(blockquote) {
  border-left: 3px solid rgb(var(--accent) / 0.5);
  margin: 0.5rem 0;
  padding: 0.15rem 0.85rem;
  color: rgb(var(--fg-muted));
}
.markdown-body :deep(table) {
  display: block;
  overflow-x: auto;
  border-collapse: collapse;
  margin: 0.6rem 0;
  font-size: 0.9rem;
}
.markdown-body :deep(thead) {
  background: rgb(var(--fg-subtle) / 0.1);
}
.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid rgb(var(--fg-subtle) / 0.25);
  padding: 0.4rem 0.65rem;
  text-align: left;
  vertical-align: top;
}
.markdown-body :deep(hr) {
  border: 0;
  border-top: 1px solid rgb(var(--fg-subtle) / 0.25);
  margin: 0.7rem 0;
}
</style>
