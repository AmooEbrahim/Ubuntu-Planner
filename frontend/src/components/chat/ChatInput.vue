<template>
  <form
    class="flex items-end gap-2 border-t border-gray-200 bg-white px-3 py-3"
    @submit.prevent="onSubmit"
  >
    <textarea
      ref="textareaEl"
      v-model="draft"
      :placeholder="placeholder"
      :disabled="disabled"
      rows="1"
      class="flex-1 resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-400 max-h-40"
      @keydown.enter.exact.prevent="onSubmit"
      @keydown.shift.enter.exact="(e) => { /* allow newline */ }"
      @input="autoResize"
    />
    <button
      v-if="streaming"
      type="button"
      class="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
      @click="$emit('cancel')"
    >Stop</button>
    <button
      v-else
      type="submit"
      :disabled="disabled || !draft.trim()"
      class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
    >Send</button>
  </form>
</template>

<script setup>
import { nextTick, ref } from 'vue'

const props = defineProps({
  disabled: { type: Boolean, default: false },
  streaming: { type: Boolean, default: false },
  placeholder: { type: String, default: 'Ask anything…' },
})

const emit = defineEmits(['send', 'cancel'])

const draft = ref('')
const textareaEl = ref(null)

const autoResize = () => {
  const el = textareaEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 160)}px`
}

const onSubmit = () => {
  if (props.disabled || props.streaming) return
  const value = draft.value.trim()
  if (!value) return
  emit('send', value)
  draft.value = ''
  nextTick(autoResize)
}
</script>
