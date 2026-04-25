<template>
  <div v-if="suggestions.length" class="flex flex-wrap gap-2 pl-11 pr-4">
    <button
      v-for="(s, idx) in suggestions"
      :key="idx"
      type="button"
      :disabled="disabled"
      class="rounded-full border border-accent/30 bg-accent/10 px-3 py-1.5 text-xs font-semibold text-accent transition-all hover:bg-accent/20 hover:border-accent/50 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
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
