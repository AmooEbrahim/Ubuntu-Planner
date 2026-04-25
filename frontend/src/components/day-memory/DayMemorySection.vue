<template>
  <section class="glass-card overflow-hidden">
    <header class="flex items-baseline justify-between px-4 pt-3 pb-2 border-b border-fg-subtle/15">
      <div>
        <h3 class="text-sm font-semibold text-fg tracking-tight">{{ title }}</h3>
        <p v-if="hint" class="text-xs text-subtle mt-0.5">{{ hint }}</p>
      </div>
      <span
        class="text-xs"
        :class="statusClass"
      >{{ statusLabel }}</span>
    </header>

    <textarea
      :value="modelValue"
      :readonly="readonly"
      :placeholder="placeholder"
      class="w-full resize-y px-4 py-3 text-sm text-fg placeholder:text-fg-subtle bg-transparent border-0 focus:outline-none focus:ring-0 min-h-[6rem]"
      :class="readonly && 'bg-fg-subtle/5'"
      rows="4"
      @input="onInput"
    />
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  title: { type: String, required: true },
  hint: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  readonly: { type: Boolean, default: false },
  status: { type: String, default: 'idle' },
})

const emit = defineEmits(['update:modelValue'])

const onInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const statusLabel = computed(() => {
  if (props.readonly) return 'Read-only'
  if (props.status === 'saving') return 'Saving…'
  if (props.status === 'saved') return 'Saved'
  if (props.status === 'error') return 'Save failed'
  return ''
})

const statusClass = computed(() => {
  if (props.readonly) return 'text-fg-subtle'
  if (props.status === 'saving') return 'text-info'
  if (props.status === 'saved') return 'text-success'
  if (props.status === 'error') return 'text-danger'
  return 'text-fg-subtle'
})
</script>
