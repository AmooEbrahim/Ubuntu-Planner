<template>
  <form
    class="flex-shrink-0 px-4 py-3"
    @submit.prevent="onSubmit"
  >
    <div class="max-w-3xl mx-auto flex items-end gap-2">
      <textarea
        ref="textareaEl"
        v-model="draft"
        :placeholder="placeholder"
        :disabled="disabled"
        rows="1"
        class="input flex-1 resize-none max-h-40 text-base"
        @keydown.enter.exact.prevent="onSubmit"
        @keydown.shift.enter.exact="(e) => { /* allow newline */ }"
        @input="autoResize"
      />
      <button
        v-if="streaming"
        type="button"
        class="btn btn-danger"
        @click="$emit('cancel')"
      >Stop</button>
      <button
        v-else
        type="submit"
        :disabled="disabled || !draft.trim()"
        class="btn btn-primary"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
        Send
      </button>
    </div>
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

defineExpose({
  focus: () => textareaEl.value?.focus(),
})
</script>
