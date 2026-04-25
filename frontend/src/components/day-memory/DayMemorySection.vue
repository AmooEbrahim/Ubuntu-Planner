<template>
  <section class="rounded-xl border border-gray-200 bg-white shadow-sm">
    <header class="flex items-baseline justify-between px-4 pt-3 pb-2 border-b border-gray-100">
      <div>
        <h3 class="text-sm font-semibold text-gray-900 tracking-tight">{{ title }}</h3>
        <p v-if="hint" class="text-xs text-gray-500 mt-0.5">{{ hint }}</p>
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
      class="w-full resize-y px-4 py-3 text-sm text-gray-800 placeholder-gray-400 bg-transparent border-0 focus:outline-none focus:ring-0 min-h-[6rem] disabled:bg-gray-50"
      :class="readonly && 'bg-gray-50/60'"
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
  if (props.readonly) return 'text-gray-400'
  if (props.status === 'saving') return 'text-blue-500'
  if (props.status === 'saved') return 'text-green-600'
  if (props.status === 'error') return 'text-red-600'
  return 'text-gray-400'
})
</script>
