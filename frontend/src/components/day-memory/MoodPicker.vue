<template>
  <div class="flex items-center gap-2">
    <span class="text-sm text-gray-600 font-medium mr-2">Mood</span>
    <button
      v-for="value in 5"
      :key="value"
      type="button"
      :disabled="disabled"
      class="h-9 w-9 rounded-full border text-base flex items-center justify-center transition focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
      :class="[
        modelValue === value
          ? 'bg-blue-500 text-white border-blue-500 shadow-sm'
          : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400 hover:text-blue-600',
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
      class="ml-2 text-xs text-gray-500 hover:text-gray-700 disabled:opacity-40 disabled:hover:text-gray-500"
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
