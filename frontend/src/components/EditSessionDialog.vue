<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import TagMultiSelect from '@/components/TagMultiSelect.vue'
import dayjs from 'dayjs'

const props = defineProps({
  session: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'saved'])

const sessionStore = useSessionStore()
const projectStore = useProjectStore()

const form = ref({
  project_id: props.session.project_id,
  start_time: props.session.start_time ? dayjs(props.session.start_time).format('YYYY-MM-DDTHH:mm') : '',
  end_time: props.session.end_time ? dayjs(props.session.end_time).format('YYYY-MM-DDTHH:mm') : '',
  planned_duration: props.session.planned_duration,
  actual_duration: props.session.actual_duration,
  satisfaction_score: props.session.satisfaction_score,
  tasks_done: props.session.tasks_done,
  notes: props.session.notes,
  tag_ids: props.session.tags ? props.session.tags.map(t => t.id) : []
})

const saving = ref(false)
const error = ref('')

onMounted(async () => {
  if (projectStore.projects.length === 0) {
    await projectStore.fetchProjects()
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''

  try {
    // Prepare data with ISO formatted times
    const updateData = {
      ...form.value,
      start_time: form.value.start_time ? dayjs(form.value.start_time).toISOString() : null,
      end_time: form.value.end_time ? dayjs(form.value.end_time).toISOString() : null
    }

    await sessionStore.updateSession(props.session.id, updateData)
    emit('saved')
    emit('close')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to update session'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="dialog-overlay" @click.self="$emit('close')">
    <div class="dialog-content">
      <div class="dialog-header">
        <h2 class="dialog-title">Edit Session</h2>
        <button @click="$emit('close')" class="close-btn" title="Close">✕</button>
      </div>

      <form @submit.prevent="handleSubmit" class="dialog-form">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- Project -->
        <div class="form-group">
          <label class="form-label">Project</label>
          <select v-model="form.project_id" class="form-select">
            <option :value="null">No Project</option>
            <option
              v-for="project in projectStore.activeProjects"
              :key="project.id"
              :value="project.id"
            >
              {{ project.name }}
            </option>
          </select>
        </div>

        <!-- Start & End Time -->
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Start Time</label>
            <input
              type="datetime-local"
              v-model="form.start_time"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">End Time</label>
            <input
              type="datetime-local"
              v-model="form.end_time"
              class="form-input"
            />
          </div>
        </div>

        <!-- Duration -->
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Planned Duration (minutes)</label>
            <input
              type="number"
              v-model.number="form.planned_duration"
              min="1"
              max="480"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">Actual Duration (minutes)</label>
            <input
              type="number"
              v-model.number="form.actual_duration"
              min="1"
              max="480"
              class="form-input"
            />
          </div>
        </div>

        <!-- Satisfaction -->
        <div class="form-group">
          <label class="form-label">
            Satisfaction: {{ form.satisfaction_score !== null ? form.satisfaction_score + '%' : 'Not set' }}
          </label>
          <input
            type="range"
            v-model.number="form.satisfaction_score"
            min="0"
            max="100"
            step="5"
            class="satisfaction-slider"
          />
          <button
            type="button"
            @click="form.satisfaction_score = null"
            class="btn-text"
          >
            Clear
          </button>
        </div>

        <!-- Tasks Done -->
        <div class="form-group">
          <label class="form-label">Tasks Accomplished</label>
          <textarea
            v-model="form.tasks_done"
            rows="3"
            class="form-textarea"
            placeholder="What did you accomplish?"
          ></textarea>
        </div>

        <!-- Notes -->
        <div class="form-group">
          <label class="form-label">Notes</label>
          <textarea
            v-model="form.notes"
            rows="3"
            class="form-textarea"
            placeholder="Any additional notes..."
          ></textarea>
        </div>

        <!-- Tags -->
        <div class="form-group">
          <label class="form-label">Tags</label>
          <TagMultiSelect v-model="form.tag_ids" />
        </div>

        <!-- Actions -->
        <div class="dialog-actions">
          <button
            type="button"
            @click="$emit('close')"
            class="btn btn-secondary"
            :disabled="saving"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="saving"
          >
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.dialog-overlay {
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
  padding: 1rem;
}

.dialog-content {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.dialog-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #111827;
}

.dialog-form {
  padding: 1.5rem;
}

.error-message {
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  color: #b91c1c;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #111827;
  background: white;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.satisfaction-slider {
  width: 100%;
  margin-bottom: 0.5rem;
}

.btn-text {
  background: none;
  border: none;
  color: #3b82f6;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0;
}

.btn-text:hover {
  color: #2563eb;
  text-decoration: underline;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 0.875rem;
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
