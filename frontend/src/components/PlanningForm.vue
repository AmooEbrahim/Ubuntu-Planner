<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="modal-overlay" @click.self="handleCancel" @keydown.escape="handleCancel">
    <div class="glass-panel w-full max-w-xl max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="flex justify-between items-center p-6 pb-4 flex-shrink-0">
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-accent/15 text-accent">
            <svg v-if="isEdit" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold text-fg">{{ isEdit ? 'Edit Planning' : 'Schedule Work' }}</h2>
            <p class="text-xs text-muted mt-0.5">{{ isEdit ? 'Update your scheduled work' : "Plan when you'll work on this" }}</p>
          </div>
        </div>
        <button @click="handleCancel" class="icon-btn" title="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div v-if="error" class="mx-6 mb-4 flex items-center gap-2 px-3 py-2 rounded-xl border border-danger/30 bg-danger/10 text-danger text-sm">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" class="flex-shrink-0">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>{{ error }}</span>
      </div>

      <form @submit.prevent="handleSubmit" class="flex flex-col flex-1 min-h-0 px-6 pb-6">
        <div class="flex-1 min-h-0 overflow-y-auto space-y-5">
          <!-- Project select -->
          <div>
            <label class="label">Project</label>
            <div ref="projectDropdownRef" class="relative cursor-pointer" @click="openProjectDropdown">
              <div
                v-if="!selectedProject"
                class="input flex items-center gap-2.5 text-subtle"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                <span class="flex-1">Select a project</span>
              </div>
              <div
                v-else
                class="input flex items-center gap-2.5"
              >
                <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: selectedProject.color }"></div>
                <span class="flex-1 truncate text-fg">{{ selectedProject.name }}</span>
                <button type="button" @click.stop="clearProject" class="text-fg-subtle hover:text-fg" title="Clear">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
              <svg class="absolute right-3 top-1/2 -translate-y-1/2 text-fg-subtle pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>

              <Transition name="dropdown">
                <div
                  v-if="projectDropdownOpen"
                  class="glass-panel absolute top-[calc(100%+6px)] left-0 right-0 z-50 overflow-hidden"
                  @click.stop
                >
                  <div class="flex items-center gap-2 px-3 py-2.5 border-b border-fg-subtle/15">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14" class="text-fg-subtle flex-shrink-0">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <input
                      v-model="projectSearch"
                      class="project-search-input flex-1 bg-transparent border-0 outline-none text-sm text-fg placeholder:text-fg-subtle"
                      placeholder="Search projects..."
                      @click.stop
                    >
                  </div>
                  <div class="max-h-48 overflow-y-auto p-1.5">
                    <button
                      v-for="p in filteredProjects"
                      :key="p.id"
                      type="button"
                      class="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-left transition-colors"
                      :class="formData.project_id === p.id
                        ? 'bg-accent/15 text-accent'
                        : 'text-fg hover:bg-fg-subtle/10'"
                      @click="selectProject(p.id)"
                    >
                      <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: p.color }"></div>
                      <span class="truncate">{{ projectStore.getProjectPath(p.id) }}</span>
                    </button>
                    <div v-if="filteredProjects.length === 0" class="p-3 text-center text-sm text-subtle">
                      No projects found
                    </div>
                  </div>
                </div>
              </Transition>
            </div>
          </div>

          <!-- Time -->
          <div>
            <label class="label">Time</label>

            <div class="flex items-end gap-3">
              <div class="flex-1 flex flex-col gap-1.5">
                <span class="text-xs text-subtle font-medium">Start</span>
                <div class="flex items-center gap-1">
                  <select v-model.number="startHour" class="input text-center text-lg font-semibold flex-1 px-2" @change="onStartTimeChange">
                    <option v-for="h in hourOptions" :key="h" :value="h">
                      {{ String(h).padStart(2, '0') }}
                    </option>
                  </select>
                  <span class="text-2xl font-bold text-fg-subtle">:</span>
                  <select v-model.number="startMinute" class="input text-center text-lg font-semibold flex-1 px-2" @change="onStartTimeChange">
                    <option v-for="m in minuteOptions" :key="m" :value="m">
                      {{ String(m).padStart(2, '0') }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="flex items-center justify-center text-fg-subtle pb-3 flex-shrink-0 hidden sm:flex">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                  <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
              </div>

              <div class="flex-1 flex flex-col gap-1.5">
                <span class="text-xs text-subtle font-medium">End</span>
                <div class="flex items-center gap-1">
                  <select v-model.number="endHour" class="input text-center text-lg font-semibold flex-1 px-2">
                    <option v-for="h in hourOptions" :key="h" :value="h">
                      {{ String(h).padStart(2, '0') }}
                    </option>
                  </select>
                  <span class="text-2xl font-bold text-fg-subtle">:</span>
                  <select v-model.number="endMinute" class="input text-center text-lg font-semibold flex-1 px-2">
                    <option v-for="m in minuteOptions" :key="m" :value="m">
                      {{ String(m).padStart(2, '0') }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between mt-3 px-4 py-2.5 rounded-xl glass-inset">
              <span class="text-sm text-muted">Duration</span>
              <span class="text-base font-bold" :style="{ color: selectedProject?.color || 'rgb(var(--accent))' }">{{ formattedDuration }}</span>
            </div>

            <div class="flex flex-wrap gap-1.5 mt-3">
              <button
                v-for="m in durationPresets"
                :key="m"
                type="button"
                class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all duration-150"
                :class="durationMinutes === m
                  ? 'bg-accent border-accent text-white'
                  : 'bg-transparent border-fg-subtle/20 text-fg-muted hover:border-accent/50 hover:text-accent'"
                @click="setDuration(m)"
              >
                {{ formatDurationLabel(m) }}
              </button>
            </div>
          </div>

          <!-- Priority -->
          <div>
            <label class="label">Priority</label>
            <div class="flex gap-2">
              <button
                type="button"
                class="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl border-2 cursor-pointer font-semibold text-sm transition-all duration-200"
                :class="formData.priority === 'low'
                  ? 'bg-fg-muted/15 border-fg-muted text-fg'
                  : 'bg-transparent border-fg-subtle/20 text-fg-muted hover:border-fg-muted/40'"
                @click="formData.priority = 'low'"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
                Low
              </button>
              <button
                type="button"
                class="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl border-2 cursor-pointer font-semibold text-sm transition-all duration-200"
                :class="formData.priority === 'medium'
                  ? 'bg-info/15 border-info text-info'
                  : 'bg-transparent border-info/30 text-info hover:border-info/60'"
                @click="formData.priority = 'medium'"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                Medium
              </button>
              <button
                type="button"
                class="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl border-2 cursor-pointer font-semibold text-sm transition-all duration-200"
                :class="formData.priority === 'critical'
                  ? 'bg-danger/15 border-danger text-danger'
                  : 'bg-transparent border-danger/30 text-danger hover:border-danger/60'"
                @click="formData.priority = 'critical'"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                  <polyline points="6 9 12 9 18 9"></polyline>
                  <polyline points="6 15 12 15 18 15"></polyline>
                </svg>
                Critical
              </button>
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="label">Description</label>
            <textarea
              v-model="formData.description"
              rows="2"
              class="input"
              placeholder="What will you work on?"
            ></textarea>
          </div>

          <!-- Tags -->
          <div>
            <label class="label">Tags</label>
            <TagMultiSelect v-model="formData.tag_ids" />
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-5 pt-4 border-t border-fg-subtle/15 flex-shrink-0">
          <button type="button" @click="handleCancel" class="btn btn-secondary">
            Cancel
          </button>
          <button type="submit" :disabled="saving || !formData.project_id" class="btn btn-primary">
            <svg v-if="saving" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="animate-spin">
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
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
