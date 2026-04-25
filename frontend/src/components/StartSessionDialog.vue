<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useProjectStore } from '@/stores/projects'
import TagMultiSelect from './TagMultiSelect.vue'
import dayjs from 'dayjs'

const emit = defineEmits(['close', 'started'])

const sessionStore = useSessionStore()
const projectStore = useProjectStore()

const selectedProjectId = ref(null)
const duration = ref(60)
const selectedTags = ref([])
const projectSearch = ref('')
const projectDropdownOpen = ref(false)
const projectDropdownRef = ref(null)
const loading = ref(false)
const error = ref('')

const selectedProject = computed(() => {
  return projectStore.projects.find(p => p.id === selectedProjectId.value)
})

const filteredProjects = computed(() => {
  const q = projectSearch.value.toLowerCase()
  return projectStore.activeProjects
    .filter(p => !q || p.name.toLowerCase().includes(q) || projectStore.getProjectPath(p.id).toLowerCase().includes(q))
    .slice(0, 15)
})

const endTime = computed(() => {
  if (!duration.value) return null
  return dayjs().add(duration.value, 'minute').format('h:mm A')
})

function openProjectDropdown() {
  projectDropdownOpen.value = true
  projectSearch.value = ''
  setTimeout(() => {
    const input = document.querySelector('.project-search-input')
    if (input) input.focus()
  }, 50)
}

function selectProject(projectId) {
  selectedProjectId.value = projectId
  const project = projectStore.projects.find(p => p.id === projectId)
  if (project?.default_duration) {
    duration.value = project.default_duration
  }
  projectDropdownOpen.value = false
  projectSearch.value = ''
}

function clearProject() {
  selectedProjectId.value = null
  projectDropdownOpen.value = false
}

function handleClickOutside(e) {
  if (projectDropdownRef.value && !projectDropdownRef.value.contains(e.target)) {
    projectDropdownOpen.value = false
  }
}

async function handleStart() {
  const sessionData = {
    project_id: selectedProjectId.value,
    planned_duration: duration.value,
    tag_ids: selectedTags.value,
  }
  try {
    loading.value = true
    error.value = ''
    await sessionStore.startSession(sessionData)
    emit('started')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Error starting session'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (projectStore.projects.length === 0) {
    await projectStore.fetchProjects()
  }
  document.addEventListener('click', handleClickOutside)
})
</script>

<template>
  <Transition name="modal">
    <div class="modal-overlay" @click.self="emit('close')" @keydown.escape="emit('close')">
      <div class="glass-panel w-full max-w-lg flex flex-col max-h-[90vh]">
        <!-- Header -->
        <div class="flex items-center justify-between gap-3 px-6 pt-6 pb-4 flex-shrink-0">
          <div class="flex items-center gap-3 min-w-0">
            <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-success/15 text-success flex-shrink-0">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
            </div>
            <div class="min-w-0">
              <h2 class="text-lg font-bold text-fg leading-tight">Start Session</h2>
              <p class="text-xs text-muted mt-0.5">Begin tracking your work time</p>
            </div>
          </div>
          <button @click="emit('close')" class="icon-btn" title="Close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- Error banner -->
        <div
          v-if="error"
          class="mx-6 mb-3 glass-card border-l-4 border-danger/60 bg-danger/5 text-danger flex items-center gap-2.5 px-4 py-2.5 text-sm flex-shrink-0"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="flex-shrink-0">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span class="flex-1">{{ error }}</span>
        </div>

        <!-- Body -->
        <form @submit.prevent="handleStart" class="flex flex-col flex-1 min-h-0 px-6 pb-6 gap-5 overflow-y-auto">
          <!-- Project -->
          <div>
            <label class="label">Project</label>
            <div ref="projectDropdownRef" class="relative cursor-pointer" @click="openProjectDropdown">
              <div
                v-if="!selectedProject"
                class="input flex items-center gap-2.5 pr-9 text-fg-subtle"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="flex-shrink-0">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>Select a project (optional)</span>
              </div>
              <div
                v-else
                class="input flex items-center gap-2.5 pr-9 text-fg"
              >
                <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: selectedProject.color }"></div>
                <span class="flex-1 truncate">{{ selectedProject.name }}</span>
                <button
                  type="button"
                  @click.stop="clearProject"
                  class="flex items-center justify-center w-5 h-5 rounded text-fg-subtle hover:text-fg hover:bg-fg-subtle/15 transition-colors flex-shrink-0"
                  title="Clear"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
              <svg
                class="absolute right-3 top-1/2 -translate-y-1/2 text-fg-subtle pointer-events-none"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"
              >
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>

              <Transition name="dropdown">
                <div
                  v-if="projectDropdownOpen"
                  class="glass-card absolute top-[calc(100%+6px)] left-0 right-0 z-50 overflow-hidden p-0"
                  @click.stop
                >
                  <div class="flex items-center gap-2 px-3 py-2.5 border-b border-fg-subtle/15">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" class="text-fg-subtle flex-shrink-0">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <input
                      v-model="projectSearch"
                      class="project-search-input flex-1 border-none outline-none text-sm bg-transparent text-fg placeholder:text-fg-subtle"
                      placeholder="Search projects..."
                      @click.stop
                    >
                  </div>
                  <div class="max-h-[200px] overflow-y-auto p-1.5">
                    <button
                      v-for="p in filteredProjects"
                      :key="p.id"
                      type="button"
                      :class="[
                        'glass-row w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-left',
                        selectedProjectId === p.id ? 'text-success font-semibold' : 'text-fg'
                      ]"
                      @click="selectProject(p.id)"
                    >
                      <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: p.color }"></div>
                      <span class="flex-1 truncate">{{ projectStore.getProjectPath(p.id) }}</span>
                      <span class="text-xs text-subtle flex-shrink-0">{{ p.default_duration }}m</span>
                    </button>
                    <div v-if="filteredProjects.length === 0" class="p-4 text-center text-sm text-subtle">
                      No projects found
                    </div>
                  </div>
                </div>
              </Transition>
            </div>
          </div>

          <!-- Duration -->
          <div>
            <label class="label">Duration</label>
            <div class="flex items-center gap-3 flex-wrap">
              <div class="relative w-28 flex-shrink-0">
                <input
                  type="number"
                  v-model.number="duration"
                  min="5"
                  step="5"
                  class="input pr-10 text-center font-semibold"
                >
                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-fg-subtle pointer-events-none">min</span>
              </div>
              <div class="flex gap-1.5 flex-wrap">
                <button
                  v-for="preset in [{ v: 30, l: '30m' }, { v: 60, l: '1h' }, { v: 90, l: '1.5h' }, { v: 120, l: '2h' }]"
                  :key="preset.v"
                  type="button"
                  @click="duration = preset.v"
                  :class="[
                    'btn btn-sm',
                    duration === preset.v ? 'btn-success' : 'btn-secondary'
                  ]"
                >
                  {{ preset.l }}
                </button>
              </div>
            </div>
            <div
              v-if="endTime"
              class="mt-2.5 flex items-center gap-1.5 px-3 py-2 rounded-xl bg-success/10 text-success text-xs"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" class="flex-shrink-0">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              Session will end at approximately <strong class="font-semibold">{{ endTime }}</strong>
            </div>
          </div>

          <!-- Tags -->
          <div>
            <label class="label">Tags</label>
            <TagMultiSelect v-model="selectedTags" />
          </div>

          <!-- Footer -->
          <div class="flex justify-end gap-2 mt-auto pt-4 border-t border-fg-subtle/15 flex-shrink-0">
            <button type="button" @click="emit('close')" class="btn btn-secondary">Cancel</button>
            <button
              type="submit"
              :disabled="!duration || loading"
              class="btn btn-success"
            >
              <svg
                v-if="loading"
                class="animate-spin"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                width="16"
                height="16"
              >
                <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="10"></circle>
              </svg>
              {{ loading ? 'Starting...' : 'Start Session' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active {
  transition: all 0.15s ease;
}
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
