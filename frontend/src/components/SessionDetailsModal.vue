<script setup>
import { ref, computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  session: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'edit', 'delete', 'update-times'])

const editingTimes = ref(false)
const startTime = ref('')
const endTime = ref('')
const saving = ref(false)

function startEditingTimes() {
  editingTimes.value = true
  startTime.value = dayjs(props.session.start_time).format('YYYY-MM-DDTHH:mm')
  if (props.session.end_time) {
    endTime.value = dayjs(props.session.end_time).format('YYYY-MM-DDTHH:mm')
  }
}

function cancelEditingTimes() {
  editingTimes.value = false
  startTime.value = ''
  endTime.value = ''
}

function saveTimeChanges() {
  saving.value = true
  // Keep the datetime-local format and let backend handle it
  emit('update-times', {
    sessionId: props.session.id,
    start_time: startTime.value ? dayjs(startTime.value).toISOString() : null,
    end_time: endTime.value ? dayjs(endTime.value).toISOString() : null
  })
  editingTimes.value = false
  saving.value = false
}

function formatTime(datetime) {
  return dayjs(datetime).format('HH:mm')
}

function formatDateTime(datetime) {
  return dayjs(datetime).format('MMM D, YYYY HH:mm')
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

const actualDuration = computed(() => {
  if (props.session.actual_duration) return props.session.actual_duration
  if (props.session.end_time) {
    const start = dayjs(props.session.start_time)
    const end = dayjs(props.session.end_time)
    return Math.floor(end.diff(start, 'minute'))
  }
  // For active sessions
  const start = dayjs(props.session.start_time)
  const now = dayjs()
  return Math.floor(now.diff(start, 'minute'))
})

const isOvertime = computed(() => {
  return actualDuration.value > props.session.planned_duration
})

const isActive = computed(() => {
  return !props.session.end_time
})
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Session Details</h2>
        <button @click="emit('close')" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <!-- Project Info -->
        <div class="info-section">
          <div class="section-label">Project</div>
          <div class="project-display" v-if="session.project">
            <span class="project-dot" :style="{ backgroundColor: session.project.color }"></span>
            <span class="project-name">{{ session.project.name }}</span>
          </div>
          <div v-else class="no-data">No Project</div>
        </div>

        <!-- Time Info -->
        <div class="info-section">
          <div class="section-header">
            <div class="section-label">Time</div>
            <button
              v-if="!editingTimes"
              @click="startEditingTimes"
              class="edit-time-btn"
              title="Edit times"
            >
              ✎ Edit
            </button>
          </div>

          <!-- View Mode -->
          <div v-if="!editingTimes" class="time-display">
            <div class="time-item">
              <span class="time-label">Started:</span>
              <span class="time-value">{{ formatDateTime(session.start_time) }}</span>
            </div>
            <div v-if="session.end_time" class="time-item">
              <span class="time-label">Ended:</span>
              <span class="time-value">{{ formatDateTime(session.end_time) }}</span>
            </div>
            <div v-else class="time-item active-indicator">
              <span class="active-badge">● Active Session</span>
            </div>
          </div>

          <!-- Edit Mode -->
          <div v-else class="time-edit">
            <div class="time-input-group">
              <label class="input-label">Start Time:</label>
              <input
                type="datetime-local"
                v-model="startTime"
                class="time-input"
              />
            </div>
            <div class="time-input-group">
              <label class="input-label">End Time:</label>
              <input
                type="datetime-local"
                v-model="endTime"
                class="time-input"
              />
            </div>
            <div class="time-edit-actions">
              <button @click="cancelEditingTimes" class="btn btn-secondary-small">Cancel</button>
              <button @click="saveTimeChanges" :disabled="saving" class="btn btn-primary-small">
                {{ saving ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Duration Info -->
        <div class="info-section">
          <div class="section-label">Duration</div>
          <div class="duration-display">
            <div class="duration-item">
              <span class="duration-label">Planned:</span>
              <span class="duration-value">{{ formatDuration(session.planned_duration) }}</span>
            </div>
            <div class="duration-item">
              <span class="duration-label">Actual:</span>
              <span class="duration-value" :class="{ overtime: isOvertime }">
                {{ formatDuration(actualDuration) }}
                <span v-if="isOvertime" class="overtime-badge">Overtime</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Tags -->
        <div v-if="session.tags && session.tags.length > 0" class="info-section">
          <div class="section-label">Tags</div>
          <div class="tags-display">
            <span
              v-for="tag in session.tags"
              :key="tag.id"
              class="tag-chip"
              :style="{ backgroundColor: tag.color }"
            >
              {{ tag.name }}
            </span>
          </div>
        </div>

        <!-- Satisfaction -->
        <div v-if="session.satisfaction_score && session.satisfaction_score > 0" class="info-section">
          <div class="section-label">Satisfaction Score</div>
          <div class="satisfaction-display">
            <div class="satisfaction-bar-container">
              <div class="satisfaction-bar" :style="{ width: session.satisfaction_score + '%' }"></div>
            </div>
            <div class="satisfaction-value">{{ session.satisfaction_score }}/100</div>
          </div>
        </div>

        <!-- Tasks Accomplished -->
        <div v-if="session.tasks_done && session.tasks_done.trim()" class="info-section">
          <div class="section-label">✓ Tasks Accomplished</div>
          <div class="content-display">{{ session.tasks_done }}</div>
        </div>

        <!-- Notes -->
        <div v-if="session.notes && session.notes.trim()" class="info-section">
          <div class="section-label">📝 Notes</div>
          <div class="content-display">{{ session.notes }}</div>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="emit('close')" class="btn btn-secondary">Close</button>
        <button @click="emit('edit', session)" class="btn btn-primary">Edit</button>
        <button @click="emit('delete', session)" class="btn btn-danger">Delete</button>
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
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 100%;
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
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6b7280;
  line-height: 1;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #111827;
}

.modal-body {
  padding: 1.5rem;
}

.info-section {
  margin-bottom: 1.5rem;
}

.info-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.section-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.edit-time-btn {
  padding: 0.375rem 0.75rem;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-time-btn:hover {
  background-color: #e5e7eb;
  border-color: #9ca3af;
}

.project-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 6px;
}

.project-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.project-name {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.no-data {
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 6px;
  color: #9ca3af;
  font-style: italic;
}

.time-display {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 6px;
}

.time-label {
  font-weight: 600;
  color: #6b7280;
  font-size: 0.875rem;
}

.time-value {
  color: #111827;
  font-size: 0.875rem;
}

.active-indicator {
  justify-content: center;
}

.active-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 1rem;
  background-color: #10b981;
  color: white;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.time-edit {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.time-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.input-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.time-input {
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #111827;
  background-color: white;
  transition: all 0.2s;
}

.time-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.time-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.btn-secondary-small,
.btn-primary-small {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 0.875rem;
}

.btn-secondary-small {
  background-color: #e5e7eb;
  color: #374151;
}

.btn-secondary-small:hover {
  background-color: #d1d5db;
}

.btn-primary-small {
  background-color: #3b82f6;
  color: white;
}

.btn-primary-small:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary-small:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.duration-display {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.duration-item {
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 6px;
  text-align: center;
}

.duration-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.duration-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: #059669;
}

.duration-value.overtime {
  color: #f59e0b;
}

.overtime-badge {
  display: block;
  font-size: 0.7rem;
  color: #f59e0b;
  font-weight: 500;
  margin-top: 0.25rem;
}

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-chip {
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

.satisfaction-display {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.satisfaction-bar-container {
  flex: 1;
  height: 12px;
  background-color: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.satisfaction-bar {
  height: 100%;
  background: linear-gradient(to right, #ef4444, #f59e0b, #10b981);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.satisfaction-value {
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
  min-width: 4rem;
  text-align: right;
}

.content-display {
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 6px;
  color: #374151;
  font-size: 0.875rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.625rem 1.25rem;
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

.btn-secondary:hover {
  background-color: #d1d5db;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
}
</style>
