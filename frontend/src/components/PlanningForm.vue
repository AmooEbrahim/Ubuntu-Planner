<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { usePlanningStore } from '@/stores/planning'
import { useProjectStore } from '@/stores/projects'
import TagMultiSelect from '@/components/TagMultiSelect.vue'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore'

dayjs.extend(utc)
dayjs.extend(isSameOrBefore)

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

const isEdit = computed(() => !!props.planning)
const error = ref('')
const saving = ref(false)
const projectSearch = ref('')
const projectDropdownOpen = ref(false)
const projectDropdownRef = ref(null)

const baseDate = computed(() => {
  if (isEdit.value && props.planning?.scheduled_start) {
    return dayjs.utc(props.planning.scheduled_start).local()
  }
  return dayjs(props.defaultDate)
})

const startHour = ref(
  isEdit.value && props.planning?.scheduled_start
    ? dayjs.utc(props.planning.scheduled_start).local().hour()
    : (props.defaultStartTime ? parseInt(props.defaultStartTime.split(':')[0]) : 9)
)

const startMinute = ref(
  isEdit.value && props.planning?.scheduled_start
    ? dayjs.utc(props.planning.scheduled_start).local().minute()
    : (props.defaultStartTime ? parseInt(props.defaultStartTime.split(':')[1]) : 0)
)

const endHour = ref(
  isEdit.value && props.planning?.scheduled_end
    ? dayjs.utc(props.planning.scheduled_end).local().hour()
    : (props.defaultStartTime ? parseInt(dayjs(props.defaultStartTime, 'HH:mm').add(1, 'hour').format('HH')) : 10)
)

const endMinute = ref(
  isEdit.value && props.planning?.scheduled_end
    ? dayjs.utc(props.planning.scheduled_end).local().minute()
    : (props.defaultStartTime ? parseInt(dayjs(props.defaultStartTime, 'HH:mm').add(1, 'hour').format('mm')) : 0)
)

const formData = ref({
  project_id: props.planning?.project_id || null,
  priority: props.planning?.priority || 'medium',
  description: props.planning?.description || '',
  tag_ids: props.planning?.tags?.map((t) => t.id) || [],
})

const durationPresets = [15, 30, 45, 60, 90, 120, 180, 240]

const hourOptions = computed(() => {
  const hours = []
  for (let h = 0; h < 24; h++) hours.push(h)
  return hours
})

const minuteOptions = [0, 15, 30, 45]

const startTimeObj = computed(() => {
  return baseDate.value.hour(startHour.value).minute(startMinute.value).second(0)
})

const endTimeObj = computed(() => {
  let end = baseDate.value.hour(endHour.value).minute(endMinute.value).second(0)
  if (end.isSameOrBefore(startTimeObj.value)) {
    end = end.add(1, 'day')
  }
  return end
})

const durationMinutes = computed(() => {
  const diff = endTimeObj.value.diff(startTimeObj.value, 'minute')
  return diff > 0 ? diff : 0
})

const formattedStartTime = computed(() => startTimeObj.value.format('h:mm A'))
const formattedEndTime = computed(() => endTimeObj.value.format('h:mm A'))
const formattedDuration = computed(() => {
  const m = durationMinutes.value
  if (m < 60) return `${m}m`
  const h = Math.floor(m / 60)
  const rm = m % 60
  return rm > 0 ? `${h}h ${rm}m` : `${h}h`
})

const selectedProject = computed(() => {
  return projectStore.projects.find(p => p.id === formData.value.project_id)
})

const filteredProjects = computed(() => {
  const q = projectSearch.value.toLowerCase()
  return projectStore.activeProjects
    .filter(p => !q || p.name.toLowerCase().includes(q) || projectStore.getProjectPath(p.id).toLowerCase().includes(q))
    .slice(0, 15)
})

function openProjectDropdown() {
  projectDropdownOpen.value = true
  projectSearch.value = ''
  nextTick(() => {
    const input = document.querySelector('.project-search-input')
    if (input) input.focus()
  })
}

function selectProject(projectId) {
  formData.value.project_id = projectId
  projectDropdownOpen.value = false
  projectSearch.value = ''
}

function clearProject() {
  formData.value.project_id = null
  projectDropdownOpen.value = false
}

function handleClickOutside(e) {
  if (projectDropdownRef.value && !projectDropdownRef.value.contains(e.target)) {
    projectDropdownOpen.value = false
  }
}

function setDuration(minutes) {
  const newEnd = startTimeObj.value.add(minutes, 'minute')
  endHour.value = newEnd.hour()
  endMinute.value = newEnd.minute()
}

function onStartTimeChange() {
  const currentDuration = durationMinutes.value
  if (currentDuration > 0) {
    const newEnd = startTimeObj.value.add(currentDuration, 'minute')
    endHour.value = newEnd.hour()
    endMinute.value = newEnd.minute()
  }
}

function formatDurationLabel(minutes) {
  if (minutes < 60) return `${minutes}m`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m > 0 ? `${h}h ${m}m` : `${h}h`
}

async function handleSubmit() {
  error.value = ''
  saving.value = true

  try {
    const submitData = {
      project_id: parseInt(formData.value.project_id),
      scheduled_start: startTimeObj.value.toISOString(),
      scheduled_end: endTimeObj.value.toISOString(),
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
  document.addEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="modal-overlay" @click.self="handleCancel" @keydown.escape="handleCancel">
    <div class="modal-container">
      <div class="modal-header">
        <div class="header-content">
          <div class="header-icon" :style="{ backgroundColor: isEdit ? '#f1f5f9' : '#eef2ff' }">
            <svg v-if="isEdit" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" width="20" height="20">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" width="20" height="20">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div>
            <h2 class="modal-title">{{ isEdit ? 'Edit Planning' : 'Schedule Work' }}</h2>
            <p class="modal-subtitle">{{ isEdit ? 'Update your scheduled work' : 'Plan when you\'ll work on this' }}</p>
          </div>
        </div>
        <button @click="handleCancel" class="close-btn" title="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div v-if="error" class="error-banner">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>{{ error }}</span>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="body-scroll">
          <div class="form-section">
            <label class="section-label">Project</label>
            <div ref="projectDropdownRef" class="project-select" @click="openProjectDropdown">
              <div v-if="!selectedProject" class="project-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>Select a project</span>
              </div>
              <div v-else class="project-selected">
                <div class="project-dot" :style="{ backgroundColor: selectedProject.color }"></div>
                <span class="project-name">{{ selectedProject.name }}</span>
                <button type="button" @click.stop="clearProject" class="project-clear" title="Clear">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
              <svg class="project-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>

              <Transition name="dropdown">
                <div v-if="projectDropdownOpen" class="project-dropdown" @click.stop>
                  <div class="project-search">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <input
                      v-model="projectSearch"
                      class="project-search-input"
                      placeholder="Search projects..."
                      @click.stop
                    >
                  </div>
                  <div class="project-list">
                    <button
                      v-for="p in filteredProjects"
                      :key="p.id"
                      type="button"
                      :class="['project-option', { active: formData.project_id === p.id }]"
                      @click="selectProject(p.id)"
                    >
                      <div class="project-dot" :style="{ backgroundColor: p.color }"></div>
                      <span>{{ projectStore.getProjectPath(p.id) }}</span>
                    </button>
                    <div v-if="filteredProjects.length === 0" class="project-empty">
                      No projects found
                    </div>
                  </div>
                </div>
              </Transition>
            </div>
          </div>

          <div class="form-section">
            <label class="section-label">Time</label>

            <div class="time-row">
              <div class="time-field">
                <span class="time-field-label">Start</span>
                <div class="time-inputs">
                  <select v-model.number="startHour" class="time-select" @change="onStartTimeChange">
                    <option v-for="h in hourOptions" :key="h" :value="h">
                      {{ String(h).padStart(2, '0') }}
                    </option>
                  </select>
                  <span class="time-sep">:</span>
                  <select v-model.number="startMinute" class="time-select" @change="onStartTimeChange">
                    <option v-for="m in minuteOptions" :key="m" :value="m">
                      {{ String(m).padStart(2, '0') }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="time-arrow">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </div>

              <div class="time-field">
                <span class="time-field-label">End</span>
                <div class="time-inputs">
                  <select v-model.number="endHour" class="time-select">
                    <option v-for="h in hourOptions" :key="h" :value="h">
                      {{ String(h).padStart(2, '0') }}
                    </option>
                  </select>
                  <span class="time-sep">:</span>
                  <select v-model.number="endMinute" class="time-select">
                    <option v-for="m in minuteOptions" :key="m" :value="m">
                      {{ String(m).padStart(2, '0') }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <div class="duration-bar">
              <span class="duration-label">Duration</span>
              <span class="duration-value" :style="{ color: selectedProject?.color || '#6366f1' }">{{ formattedDuration }}</span>
            </div>

            <div class="duration-presets">
              <button
                v-for="m in durationPresets"
                :key="m"
                type="button"
                :class="['preset-btn', { active: durationMinutes === m }]"
                @click="setDuration(m)"
              >
                {{ formatDurationLabel(m) }}
              </button>
            </div>
          </div>

          <div class="form-section">
            <label class="section-label">Priority</label>
            <div class="priority-buttons">
              <button
                type="button"
                :class="['priority-btn', 'priority-low', { active: formData.priority === 'low' }]"
                @click="formData.priority = 'low'"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
                Low
              </button>
              <button
                type="button"
                :class="['priority-btn', 'priority-medium', { active: formData.priority === 'medium' }]"
                @click="formData.priority = 'medium'"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                Medium
              </button>
              <button
                type="button"
                :class="['priority-btn', 'priority-critical', { active: formData.priority === 'critical' }]"
                @click="formData.priority = 'critical'"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <polyline points="6 9 12 9 18 9"></polyline>
                  <polyline points="6 15 12 15 18 15"></polyline>
                </svg>
                Critical
              </button>
            </div>
          </div>

          <div class="form-section">
            <label class="section-label">Description</label>
            <textarea
              v-model="formData.description"
              rows="2"
              class="form-textarea"
              placeholder="What will you work on?"
            ></textarea>
          </div>

          <div class="form-section">
            <label class="section-label">Tags</label>
            <TagMultiSelect v-model="formData.tag_ids" />
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" @click="handleCancel" class="btn-secondary">
            Cancel
          </button>
          <button type="submit" :disabled="saving || !formData.project_id" class="btn-primary">
            <svg v-if="saving" class="btn-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="10"></circle>
            </svg>
            {{ saving ? 'Saving...' : (isEdit ? 'Save Changes' : 'Schedule') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-container {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 520px;
  height: 600px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0.125rem 0 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: #f1f5f9;
  border-radius: 10px;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  margin: 0 1.5rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #dc2626;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.modal-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 0 1.5rem 1.5rem;
}

.body-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.section-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.project-select {
  position: relative;
  cursor: pointer;
}

.project-placeholder,
.project-selected {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #0f172a;
  background: white;
  transition: all 0.2s ease;
}

.project-placeholder {
  color: #94a3b8;
}

.project-select:hover .project-placeholder,
.project-select:hover .project-selected {
  border-color: #cbd5e1;
}

.project-select:focus-within .project-placeholder,
.project-select:focus-within .project-selected {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.project-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.project-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-clear {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.project-clear:hover {
  background: #f1f5f9;
  color: #64748b;
}

.project-chevron {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #94a3b8;
  pointer-events: none;
}

.project-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  z-index: 200;
  overflow: hidden;
}

.project-search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.project-search svg {
  color: #94a3b8;
  flex-shrink: 0;
}

.project-search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.875rem;
  color: #0f172a;
  background: transparent;
}

.project-search-input::placeholder {
  color: #94a3b8;
}

.project-list {
  max-height: 180px;
  overflow-y: auto;
  padding: 0.375rem;
}

.project-option {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.625rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.project-option:hover {
  background: #f8fafc;
}

.project-option.active {
  background: #eef2ff;
  color: #6366f1;
}

.project-empty {
  padding: 1rem;
  text-align: center;
  font-size: 0.85rem;
  color: #94a3b8;
}

.time-row {
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
}

.time-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.time-field-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
}

.time-inputs {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.time-select {
  flex: 1;
  padding: 0.625rem 0.375rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #0f172a;
  background: white;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  -moz-appearance: textfield;
}

.time-select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.time-sep {
  font-size: 1.5rem;
  font-weight: 700;
  color: #cbd5e1;
  padding: 0 0.125rem;
}

.time-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #cbd5e1;
  padding-bottom: 0.25rem;
  flex-shrink: 0;
}

.duration-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 1rem;
  background: #f8fafc;
  border-radius: 10px;
}

.duration-label {
  font-size: 0.85rem;
  color: #64748b;
}

.duration-value {
  font-size: 1.1rem;
  font-weight: 700;
}

.duration-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.preset-btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preset-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.preset-btn.active {
  background: #6366f1;
  border-color: #6366f1;
  color: white;
}

.priority-buttons {
  display: flex;
  gap: 0.5rem;
}

.priority-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.625rem;
  border: 2px solid;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  background: white;
}

.priority-low {
  border-color: #e2e8f0;
  color: #64748b;
}

.priority-low.active {
  background: #f1f5f9;
  border-color: #64748b;
  color: #334155;
}

.priority-medium {
  border-color: #bfdbfe;
  color: #3b82f6;
}

.priority-medium.active {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1d4ed8;
}

.priority-critical {
  border-color: #fecaca;
  color: #ef4444;
}

.priority-critical.active {
  background: #fef2f2;
  border-color: #ef4444;
  color: #dc2626;
}

.form-textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #0f172a;
  background: white;
  transition: all 0.2s ease;
  resize: vertical;
  font-family: inherit;
}

.form-textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-textarea::placeholder {
  color: #94a3b8;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.btn-secondary {
  padding: 0.75rem 1.25rem;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 640px) {
  .modal-container {
    border-radius: 16px;
    margin: 0.5rem;
  }

  .time-row {
    flex-wrap: wrap;
  }

  .time-arrow {
    display: none;
  }
}
</style>
