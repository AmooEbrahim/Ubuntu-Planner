<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanningStore } from '@/stores/planning'
import { useProjectStore } from '@/stores/projects'
import dayjs from 'dayjs'
import TagSelector from '@/components/TagSelector.vue'

const props = defineProps({
  planning: {
    type: Object,
    default: null,
  },
  defaultDate: {
    type: Object,
    default: () => dayjs(),
  },
  defaultStartTime: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['close', 'saved'])

const planningStore = usePlanningStore()
const projectStore = useProjectStore()

const formData = ref({
  project_id: props.planning?.project_id || null,
  scheduled_start: props.planning?.scheduled_start ||
    (props.defaultStartTime
      ? dayjs(props.defaultDate).format('YYYY-MM-DD') + 'T' + props.defaultStartTime
      : dayjs(props.defaultDate).hour(9).minute(0).format('YYYY-MM-DDTHH:mm')),
  scheduled_end: props.planning?.scheduled_end ||
    (props.defaultStartTime
      ? dayjs(props.defaultDate).format('YYYY-MM-DD') + 'T' + dayjs(props.defaultStartTime, 'HH:mm').add(1, 'hour').format('HH:mm')
      : dayjs(props.defaultDate).hour(10).minute(0).format('YYYY-MM-DDTHH:mm')),
  priority: props.planning?.priority || 'medium',
  description: props.planning?.description || '',
  tag_ids: props.planning?.tags?.map((t) => t.id) || [],
})

const isEdit = computed(() => !!props.planning)
const error = ref('')
const saving = ref(false)

const durationMinutes = computed(() => {
  const start = dayjs(formData.value.scheduled_start)
  const end = dayjs(formData.value.scheduled_end)
  return end.diff(start, 'minute')
})

function addDuration(minutes) {
  const start = dayjs(formData.value.scheduled_start)
  formData.value.scheduled_end = start.add(minutes, 'minute').format('YYYY-MM-DDTHH:mm')
}

function setDuration(minutes) {
  const start = dayjs(formData.value.scheduled_start)
  formData.value.scheduled_end = start.add(minutes, 'minute').format('YYYY-MM-DDTHH:mm')
}

async function handleSubmit() {
  error.value = ''
  saving.value = true

  try {
    // Prepare data for API
    const submitData = {
      project_id: parseInt(formData.value.project_id),
      scheduled_start: dayjs(formData.value.scheduled_start).toISOString(),
      scheduled_end: dayjs(formData.value.scheduled_end).toISOString(),
      priority: formData.value.priority,
      description: formData.value.description,
      tag_ids: formData.value.tag_ids,
    }

    if (isEdit.value) {
      await planningStore.updatePlanning(props.planning.id, submitData)
    } else {
      await planningStore.createPlanning(submitData)
    }
    emit('saved')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Error saving planning'
  } finally {
    saving.value = false
  }
}

function handleCancel() {
  emit('close')
}

onMounted(async () => {
  if (projectStore.projects.length === 0) {
    await projectStore.fetchProjects()
  }
})
</script>

<template>
  <div class="modal-overlay" @click.self="handleCancel">
    <div class="modal-content">
      <div class="modal-header">
        <h2 class="text-2xl font-bold">{{ isEdit ? 'Edit' : 'Create' }} Planning</h2>
        <button @click="handleCancel" class="close-btn">&times;</button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="form-group">
          <label class="form-label">Project <span class="required">*</span></label>
          <select v-model="formData.project_id" required class="form-select">
            <option :value="null" disabled>Select a project</option>
            <option
              v-for="project in projectStore.activeProjects"
              :key="project.id"
              :value="project.id"
            >
              {{ project.name }}
            </option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Start Time <span class="required">*</span></label>
            <input
              type="datetime-local"
              v-model="formData.scheduled_start"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="form-label">End Time <span class="required">*</span></label>
            <input
              type="datetime-local"
              v-model="formData.scheduled_end"
              required
              class="form-input"
            />
          </div>
        </div>

        <div class="duration-info">
          <span class="text-sm text-gray-600">Duration: {{ durationMinutes }} minutes</span>
          <div class="quick-durations">
            <button type="button" @click="setDuration(30)" class="duration-btn">30m</button>
            <button type="button" @click="setDuration(60)" class="duration-btn">1h</button>
            <button type="button" @click="setDuration(90)" class="duration-btn">1.5h</button>
            <button type="button" @click="setDuration(120)" class="duration-btn">2h</button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Priority</label>
          <div class="priority-buttons">
            <button
              type="button"
              :class="['priority-btn', 'priority-low', { active: formData.priority === 'low' }]"
              @click="formData.priority = 'low'"
            >
              Low
            </button>
            <button
              type="button"
              :class="[
                'priority-btn',
                'priority-medium',
                { active: formData.priority === 'medium' },
              ]"
              @click="formData.priority = 'medium'"
            >
              Medium
            </button>
            <button
              type="button"
              :class="[
                'priority-btn',
                'priority-critical',
                { active: formData.priority === 'critical' },
              ]"
              @click="formData.priority = 'critical'"
            >
              Critical
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Description</label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="form-textarea"
            placeholder="Optional description..."
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">Tags</label>
          <TagSelector :project-id="formData.project_id" v-model="formData.tag_ids" />
        </div>

        <div class="form-actions">
          <button type="button" @click="handleCancel" class="btn btn-secondary">Cancel</button>
          <button type="submit" :disabled="saving" class="btn btn-primary">
            {{ saving ? 'Saving...' : 'Save Planning' }}
          </button>
        </div>
      </form>
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
  z-index: 1000;
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

.form-group {
  margin-bottom: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.required {
  color: #ef4444;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.9rem;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.duration-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  padding: 0.75rem;
  background-color: #f3f4f6;
  border-radius: 4px;
}

.quick-durations {
  display: flex;
  gap: 0.5rem;
}

.duration-btn {
  padding: 0.375rem 0.75rem;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.duration-btn:hover {
  background-color: #e5e7eb;
}

.priority-buttons {
  display: flex;
  gap: 0.75rem;
}

.priority-btn {
  flex: 1;
  padding: 0.625rem;
  border: 2px solid;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  background-color: white;
}

.priority-low {
  border-color: #6b7280;
  color: #6b7280;
}

.priority-low.active {
  background-color: #6b7280;
  color: white;
}

.priority-medium {
  border-color: #3b82f6;
  color: #3b82f6;
}

.priority-medium.active {
  background-color: #3b82f6;
  color: white;
}

.priority-critical {
  border-color: #ef4444;
  color: #ef4444;
}

.priority-critical.active {
  background-color: #ef4444;
  color: white;
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

.btn-secondary:hover {
  background-color: #d1d5db;
}

.btn-primary {
  background-color: #10b981;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #059669;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
