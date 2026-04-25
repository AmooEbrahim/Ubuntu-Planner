<script setup>
import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import TagMultiSelect from '@/components/TagMultiSelect.vue'

const props = defineProps({
  session: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'saved'])

const sessionStore = useSessionStore()

const formData = ref({
  satisfaction_score: props.session.satisfaction_score || 80,
  tasks_done: props.session.tasks_done || '',
  notes: props.session.notes || '',
  tag_ids: props.session.tags?.map((t) => t.id) || [],
})

const saving = ref(false)
const error = ref('')

const actualDuration = computed(() => {
  const start = new Date(props.session.start_time)
  const now = new Date()
  return Math.floor((now - start) / 1000 / 60)
})

const plannedDuration = computed(() => props.session.planned_duration)
const isOvertime = computed(() => actualDuration.value > plannedDuration.value)

async function handleSave() {
  saving.value = true
  error.value = ''
  try {
    await sessionStore.stopSession(props.session.id, formData.value)
    emit('saved')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Error saving review'
  } finally {
    saving.value = false
  }
}

async function handleQuickSave() {
  saving.value = true
  error.value = ''
  try {
    await sessionStore.stopSession(props.session.id)
    emit('saved')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Error stopping session'
  } finally {
    saving.value = false
  }
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="glass-panel w-full max-w-xl max-h-[90vh] flex flex-col overflow-hidden">
      <div class="flex justify-between items-center p-6 border-b border-fg-subtle/15">
        <h2 class="text-xl font-bold text-fg">Session Review</h2>
        <button @click="emit('close')" class="icon-btn" title="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="p-6 overflow-y-auto flex-1">
        <div v-if="error" class="mb-4 p-3 rounded-xl border border-danger/30 bg-danger/10 text-danger text-sm">
          {{ error }}
        </div>

        <div class="glass-inset p-4 mb-6 space-y-1.5">
          <div class="flex justify-between">
            <span class="font-semibold text-muted">Project:</span>
            <span class="font-semibold text-fg">{{ session.project?.name || 'No Project' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="font-semibold text-muted">Actual Duration:</span>
            <span class="font-semibold" :class="isOvertime ? 'text-danger' : 'text-fg'">
              {{ formatDuration(actualDuration) }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="font-semibold text-muted">Planned Duration:</span>
            <span class="font-semibold text-fg">{{ formatDuration(plannedDuration) }}</span>
          </div>
          <div v-if="isOvertime" class="flex justify-between mt-2 pt-2 border-t border-fg-subtle/15 text-danger">
            <span class="font-semibold">Overtime:</span>
            <span class="font-semibold">{{ formatDuration(actualDuration - plannedDuration) }}</span>
          </div>
        </div>

        <form @submit.prevent="handleSave" class="space-y-5">
          <div>
            <label class="label">
              Satisfaction (0-100): <strong class="text-accent">{{ formData.satisfaction_score }}</strong>
            </label>
            <input
              type="range"
              v-model.number="formData.satisfaction_score"
              min="0"
              max="100"
              class="satisfaction-slider w-full h-2 rounded-full outline-none appearance-none"
            />
            <div class="flex justify-between mt-2 text-xs text-muted">
              <span>😞 Not Satisfied</span>
              <span>😊 Very Satisfied</span>
            </div>
          </div>

          <div>
            <label class="label">What did you accomplish?</label>
            <textarea
              v-model="formData.tasks_done"
              rows="4"
              class="input"
              placeholder="Describe what you completed during this session..."
            ></textarea>
          </div>

          <div>
            <label class="label">Additional notes</label>
            <textarea
              v-model="formData.notes"
              rows="3"
              class="input"
              placeholder="Any additional thoughts or observations..."
            ></textarea>
          </div>

          <div>
            <label class="label">Tags</label>
            <TagMultiSelect v-model="formData.tag_ids" />
          </div>

          <div class="flex justify-end gap-2 mt-6 pt-6 border-t border-fg-subtle/15">
            <button type="button" @click="handleQuickSave" :disabled="saving" class="btn btn-secondary">
              {{ saving ? 'Saving...' : 'Save Without Review' }}
            </button>
            <button type="submit" :disabled="saving" class="btn btn-success">
              {{ saving ? 'Saving...' : 'Save Review' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.satisfaction-slider {
  background: linear-gradient(to right, rgb(var(--danger)), rgb(var(--warning)), rgb(var(--success)));
}
.satisfaction-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: white;
  border: 3px solid rgb(var(--success));
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
.satisfaction-slider::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: white;
  border: 3px solid rgb(var(--success));
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
</style>
