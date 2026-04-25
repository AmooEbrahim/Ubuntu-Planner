<template>
  <div class="flex gap-3" :class="alignClass">
    <div
      v-if="role !== 'user'"
      class="flex-shrink-0 h-7 w-7 rounded-full bg-gray-100 text-gray-500 text-[11px] font-semibold flex items-center justify-center select-none"
    >{{ avatarText }}</div>

    <div class="max-w-[75%] min-w-0 space-y-1.5">
      <div
        class="rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm"
        :class="bubbleClass"
      >
        <div
          v-if="role === 'user'"
          class="whitespace-pre-wrap"
        >{{ content || '…' }}</div>
        <div
          v-else
          class="markdown-body"
          v-html="renderedHtml"
        />
        <span v-if="streaming" class="inline-block w-1 h-4 bg-current align-middle animate-pulse ml-0.5" />
      </div>
      <div v-if="meta" class="text-[10px] text-gray-400 px-1">{{ meta }}</div>
    </div>

    <div
      v-if="role === 'user'"
      class="flex-shrink-0 h-7 w-7 rounded-full bg-blue-100 text-blue-600 text-[11px] font-semibold flex items-center justify-center select-none"
    >{{ avatarText }}</div>
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
const bubbleClass = computed(() => {
  if (props.role === 'user') return 'bg-blue-600 text-white'
  return 'bg-white border border-gray-200 text-gray-900'
})
const avatarText = computed(() => (props.role === 'user' ? 'You' : 'AI'))

const renderedHtml = computed(() => {
  const text = props.content || (props.streaming ? '' : '…')
  if (!text) return ''
  return md.render(text)
})
</script>

<style scoped>
.markdown-body :deep(p) { margin: 0.25rem 0; }
.markdown-body :deep(p:first-child) { margin-top: 0; }
.markdown-body :deep(p:last-child) { margin-bottom: 0; }
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  font-weight: 600;
  margin: 0.5rem 0 0.25rem;
  line-height: 1.3;
}
.markdown-body :deep(h1) { font-size: 1.05rem; }
.markdown-body :deep(h2) { font-size: 1rem; }
.markdown-body :deep(h3) { font-size: 0.95rem; }
.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0.25rem 0 0.25rem 1.25rem;
  padding: 0;
}
.markdown-body :deep(li) { margin: 0.1rem 0; }
.markdown-body :deep(li > p) { margin: 0; }
.markdown-body :deep(strong) { font-weight: 600; }
.markdown-body :deep(em) { font-style: italic; }
.markdown-body :deep(a) {
  color: rgb(37 99 235);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.markdown-body :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.85em;
  background: rgb(243 244 246);
  border-radius: 0.25rem;
  padding: 0.05rem 0.3rem;
}
.markdown-body :deep(pre) {
  background: rgb(17 24 39);
  color: rgb(229 231 235);
  border-radius: 0.5rem;
  padding: 0.65rem 0.85rem;
  overflow-x: auto;
  margin: 0.5rem 0;
  font-size: 0.8rem;
  line-height: 1.45;
}
.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}
.markdown-body :deep(blockquote) {
  border-left: 3px solid rgb(209 213 219);
  margin: 0.4rem 0;
  padding: 0.1rem 0.75rem;
  color: rgb(75 85 99);
}
.markdown-body :deep(table) {
  display: block;
  overflow-x: auto;
  border-collapse: collapse;
  margin: 0.5rem 0;
  font-size: 0.82rem;
}
.markdown-body :deep(thead) {
  background: rgb(249 250 251);
}
.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid rgb(229 231 235);
  padding: 0.35rem 0.6rem;
  text-align: left;
  vertical-align: top;
}
.markdown-body :deep(hr) {
  border: 0;
  border-top: 1px solid rgb(229 231 235);
  margin: 0.6rem 0;
}
</style>
