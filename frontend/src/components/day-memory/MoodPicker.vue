<template>
  <div class="flex items-center gap-2 flex-wrap">
    <span class="text-sm text-muted font-medium mr-2">Mood</span>
    <button
      v-for="value in 5"
      :key="value"
      type="button"
      :disabled="disabled"
      class="h-9 w-9 rounded-full border text-base flex items-center justify-center transition-all focus:outline-none"
      :class="[
        modelValue === value
          ? 'bg-accent text-white border-accent shadow-sm shadow-accent/30'
          : 'bg-white/40 dark:bg-white/5 text-fg-muted border-fg-subtle/30 hover:border-accent hover:text-accent',
        disabled && 'opacity-60 cursor-not-allowed',
      ]"
      :aria-label="moodLabel(value)"
      :title="moodLabel(value)"
      @click="select(value)"
    >
      {{ moodEmoji(value) }}
    </button>
    <button
      type="button"
      :disabled="disabled || modelValue == null"
      class="ml-2 text-xs text-muted hover:text-fg disabled:opacity-40 disabled:hover:text-fg-muted transition-colors"
      @click="select(null)"
    >
      Clear
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Number, default: null },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const MOOD_EMOJI = ['😞', '🙁', '😐', '🙂', '😄']
const MOOD_LABEL = ['Awful', 'Down', 'Okay', 'Good', 'Great']

const moodEmoji = (v) => MOOD_EMOJI[v - 1]
const moodLabel = (v) => MOOD_LABEL[v - 1]

const select = (value) => {
  if (props.disabled) return
  emit('update:modelValue', value)
}
</script>
