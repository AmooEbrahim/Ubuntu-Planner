<script setup>
import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import TagSelector from '@/components/TagSelector.vue'

const props = defineProps({
  session: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'saved'])

const sessionStore = useSessionStore()

const formData = ref({
  satisfaction_score: 80,
  tasks_done: '',
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
    <div class="modal-content">
      <div class="modal-header">
        <h2>Session Review</h2>
        <button @click="emit('close')" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="session-summary">
          <div class="summary-item">
            <span class="label">Project:</span>
            <span class="value">{{ session.project?.name || 'No Project' }}</span>
          </div>
          <div class="summary-item">
            <span class="label">Actual Duration:</span>
            <span class="value" :class="{ overtime: isOvertime }">
              {{ formatDuration(actualDuration) }}
            </span>
          </div>
          <div class="summary-item">
            <span class="label">Planned Duration:</span>
            <span class="value">{{ formatDuration(plannedDuration) }}</span>
          </div>
          <div v-if="isOvertime" class="summary-item overtime-notice">
            <span class="label">Overtime:</span>
            <span class="value">{{ formatDuration(actualDuration - plannedDuration) }}</span>
          </div>
        </div>

        <form @submit.prevent="handleSave">
          <div class="form-group">
            <label class="form-label">
              Satisfaction (0-100): <strong>{{ formData.satisfaction_score }}</strong>
            </label>
            <input
              type="range"
              v-model.number="formData.satisfaction_score"
              min="0"
              max="100"
              class="satisfaction-slider"
            />
            <div class="satisfaction-labels">
              <span>😞 Not Satisfied</span>
              <span>😊 Very Satisfied</span>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">What did you accomplish?</label>
            <textarea
              v-model="formData.tasks_done"
              rows="4"
              class="form-textarea"
              placeholder="Describe what you completed during this session..."
            ></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">Additional notes</label>
            <textarea
              v-model="formData.notes"
              rows="3"
              class="form-textarea"
              placeholder="Any additional thoughts or observations..."
            ></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">Tags</label>
            <TagSelector :project-id="session.project_id" v-model="formData.tag_ids" />
          </div>

          <div class="form-actions">
            <button type="button" @click="handleQuickSave" :disabled="saving" class="btn btn-secondary">
              {{ saving ? 'Saving...' : 'Save Without Review' }}
            </button>
            <button type="submit" :disabled="saving" class="btn btn-primary">
              {{ saving ? 'Saving...' : 'Save Review' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6b7280;
  line-height: 1;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.error-message {
  padding: 0.75rem;
  margin-bottom: 1rem;
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #b91c1c;
  border-radius: 4px;
  font-size: 0.9rem;
}

.session-summary {
  background-color: #f9fafb;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-item.overtime-notice {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
  color: #ef4444;
}

.label {
  font-weight: 600;
  color: #6b7280;
}

.value {
  font-weight: 600;
  color: #111827;
}

.value.overtime {
  color: #ef4444;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.satisfaction-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(to right, #ef4444, #f59e0b, #10b981);
  outline: none;
  -webkit-appearance: none;
}

.satisfaction-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  border: 3px solid #10b981;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.satisfaction-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  border: 3px solid #10b981;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.satisfaction-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #6b7280;
}

.form-textarea {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background-color: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #d1d5db;
}

.btn-primary {
  background-color: #10b981;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #059669;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
