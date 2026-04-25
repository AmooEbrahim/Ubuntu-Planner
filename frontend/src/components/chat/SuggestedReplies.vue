<template>
  <div v-if="suggestions.length" class="flex flex-wrap gap-2 pl-10 pr-4">
    <button
      v-for="(s, idx) in suggestions"
      :key="idx"
      type="button"
      :disabled="disabled"
      class="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 transition hover:bg-blue-100 hover:border-blue-300 disabled:opacity-50 disabled:cursor-not-allowed"
      @click="$emit('pick', s)"
    >{{ s }}</button>
  </div>
</template>

<script setup>
defineProps({
  suggestions: { type: Array, default: () => [] },
  disabled: { type: Boolean, default: false },
})
defineEmits(['pick'])
</script>
