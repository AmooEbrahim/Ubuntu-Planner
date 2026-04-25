<template>
  <div class="space-y-4">
    <div v-if="track === 'ai' && readonly" class="glass-card border-l-4 border-warning/60 bg-warning/5 flex items-start gap-3 px-4 py-3 text-sm text-warning">
      <svg class="h-5 w-5 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m0 3.75h.008M21.75 12a9.75 9.75 0 1 1-19.5 0 9.75 9.75 0 0 1 19.5 0Z"/></svg>
      <div class="flex-1">
        <p class="font-semibold">AI track is read-only.</p>
        <p class="mt-1 opacity-90">The AI writes here on its own. To edit by hand, enable the override below.</p>
      </div>
      <button
        type="button"
        class="btn btn-sm bg-warning text-white hover:opacity-90"
        @click="$emit('toggle-readonly')"
      >Edit anyway</button>
    </div>

    <MoodPicker
      :model-value="entry?.mood ?? null"
      :disabled="readonly"
      @update:model-value="(v) => onFieldUpdate('mood', v, { immediate: true })"
    />

    <DayMemorySection
      v-for="section in SECTIONS"
      :key="section.key"
      :title="section.title"
      :hint="section.hint"
      :placeholder="section.placeholder"
      :readonly="readonly"
      :status="statuses[section.key] ?? 'idle'"
      :model-value="entry?.[section.key] ?? ''"
      @update:model-value="(v) => onFieldUpdate(section.key, v)"
    />
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import MoodPicker from './MoodPicker.vue'
import DayMemorySection from './DayMemorySection.vue'
import { useDayMemoryStore } from '@/stores/dayMemory'

const SECTIONS = [
  { key: 'intentions', title: 'How do you want to go in this day?', hint: 'Set a clear intention before the day starts.', placeholder: 'I want to focus on…' },
  { key: 'completed', title: 'What did you complete today?', hint: 'Concrete things that got done.', placeholder: '— Shipped phase 1\n— Reviewed plan\n…' },
  { key: 'reflection', title: 'How did it actually happen?', hint: 'Honest summary, not a to-do list.', placeholder: 'The morning went well, then…' },
  { key: 'lessons', title: 'What did you learn from this day?', hint: 'Insight you want to remember.', placeholder: 'I noticed that…' },
  { key: 'gratitude', title: 'Thanksgiving', hint: 'Things, people, or moments you are grateful for.', placeholder: 'I am grateful for…' },
  { key: 'free_notes', title: 'Anything else', hint: 'Free-form notes for the day.', placeholder: '' },
]

const props = defineProps({
  date: { type: String, required: true },
  track: { type: String, required: true },
  readonly: { type: Boolean, default: false },
  entry: { type: Object, default: null },
})

defineEmits(['toggle-readonly'])

const store = useDayMemoryStore()
const statuses = reactive({})

const debouncedSavers = new Map()

const getDebouncedSaver = (field) => {
  if (!debouncedSavers.has(field)) {
    debouncedSavers.set(
      field,
      useDebounceFn((value) => commitSave(field, value), 600),
    )
  }
  return debouncedSavers.get(field)
}

const commitSave = async (field, value) => {
  if (props.readonly) return
  statuses[field] = 'saving'
  try {
    await store.upsert(props.date, props.track, { [field]: value })
    statuses[field] = 'saved'
    setTimeout(() => {
      if (statuses[field] === 'saved') statuses[field] = 'idle'
    }, 1500)
  } catch (error) {
    statuses[field] = 'error'
  }
}

const onFieldUpdate = (field, value, options = {}) => {
  store.setLocalField(props.date, props.track, field, value)
  if (props.readonly) return
  if (options.immediate) {
    commitSave(field, value)
  } else {
    statuses[field] = 'saving'
    getDebouncedSaver(field)(value)
  }
}

watch(
  () => `${props.date}:${props.track}`,
  () => {
    Object.keys(statuses).forEach((k) => delete statuses[k])
  },
)
</script>
