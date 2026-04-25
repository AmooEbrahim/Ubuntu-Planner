<script setup>
import { ref, computed } from 'vue'
import { useProjectStore } from '@/stores/projects'

const props = defineProps({
  project: Object,
  parentProject: Object
})

const emit = defineEmits(['close', 'saved'])

const projectStore = useProjectStore()

const formData = ref({
  name: props.project?.name || '',
  parent_id: props.project?.parent_id || props.parentProject?.id || null,
  color: props.project?.color || '#6366f1',
  description: props.project?.description || '',
  default_duration: props.project?.default_duration || 60,
  notification_interval: props.project?.notification_interval || null,
  is_pinned: props.project?.is_pinned || false
})

const isEdit = computed(() => !!props.project)
const saving = ref(false)
const error = ref(null)
const activeTab = ref('details')

const presetColors = [
  '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
  '#ec4899', '#f43f5e', '#ef4444', '#f97316',
  '#f59e0b', '#eab308', '#84cc16', '#22c55e',
  '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
  '#3b82f6', '#2563eb', '#4f46e5', '#7c3aed'
]

const parentSearchQuery = ref('')
const parentDropdownOpen = ref(false)
const parentDropdownRef = ref(null)

const parentOptions = computed(() => {
  const q = parentSearchQuery.value.toLowerCase()
  const currentId = isEdit.value ? props.project?.id : null
  return projectStore.activeProjects
    .filter(p => p.id !== currentId)
    .filter(p => !q || projectStore.getProjectPath(p.id).toLowerCase().includes(q))
    .slice(0, 20)
})

const selectedParent = computed(() => {
  if (!formData.value.parent_id) return null
  return projectStore.activeProjects.find(p => p.id === formData.value.parent_id)
})

function openParentDropdown() {
  parentDropdownOpen.value = true
  parentSearchQuery.value = ''
  setTimeout(() => {
    const input = document.querySelector('.parent-search-input')
    if (input) input.focus()
  }, 50)
}

function selectParent(project) {
  formData.value.parent_id = project ? project.id : null
  parentDropdownOpen.value = false
  parentSearchQuery.value = ''
}

function clearParent() {
  formData.value.parent_id = null
  parentDropdownOpen.value = false
}

function handleClickOutside(e) {
  if (parentDropdownRef.value && !parentDropdownRef.value.contains(e.target)) {
    parentDropdownOpen.value = false
  }
}

if (typeof window !== 'undefined') {
  document.addEventListener('click', handleClickOutside)
}

async function handleSubmit() {
  saving.value = true
  error.value = null
  try {
    if (isEdit.value) {
      await projectStore.updateProject(props.project.id, formData.value)
    } else {
      await projectStore.createProject(formData.value)
    }
    emit('saved')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')" @keydown.escape="emit('close')">
    <div class="glass-panel w-full max-w-lg flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="flex items-center justify-between gap-3 px-6 pt-6 pb-4 flex-shrink-0">
        <div class="flex items-center gap-3 min-w-0">
          <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-accent/15 text-accent flex-shrink-0">
            <svg v-if="isEdit" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </div>
          <div class="min-w-0">
            <h2 class="text-lg font-bold text-fg leading-tight">{{ isEdit ? 'Edit Project' : 'Create Project' }}</h2>
            <p class="text-xs text-muted mt-0.5">{{ isEdit ? 'Update project settings' : 'Set up a new project to track' }}</p>
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

      <!-- Tabs -->
      <div class="mx-6 mb-3 glass-inset flex gap-1 p-1 flex-shrink-0">
        <button
          type="button"
          :class="[
            'flex-1 inline-flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200',
            activeTab === 'details'
              ? 'bg-accent/15 text-accent'
              : 'text-fg-muted hover:text-fg'
          ]"
          @click="activeTab = 'details'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          Details
        </button>
        <button
          type="button"
          :class="[
            'flex-1 inline-flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200',
            activeTab === 'settings'
              ? 'bg-accent/15 text-accent'
              : 'text-fg-muted hover:text-fg'
          ]"
          @click="activeTab = 'settings'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          Settings
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="flex flex-col flex-1 min-h-0 px-6 pb-6">
        <div class="flex-1 min-h-0 overflow-y-auto pr-1">
          <div v-show="activeTab === 'details'" class="flex flex-col gap-5">
            <div>
              <label class="label">Project Name</label>
              <input
                v-model="formData.name"
                required
                placeholder="e.g., Website Redesign"
                class="input"
              >
            </div>

            <div>
              <label class="label">Description</label>
              <textarea
                v-model="formData.description"
                rows="3"
                placeholder="What is this project about?"
                class="input"
              ></textarea>
            </div>

            <div>
              <label class="label">Color</label>
              <div class="flex flex-col gap-3">
                <div class="grid grid-cols-10 gap-2">
                  <button
                    v-for="color in presetColors"
                    :key="color"
                    type="button"
                    class="aspect-square rounded-lg transition-all duration-150 hover:scale-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent"
                    :class="formData.color === color ? 'ring-2 ring-fg ring-offset-2 ring-offset-transparent' : ''"
                    :style="{ backgroundColor: color }"
                    @click="formData.color = color"
                    :title="color"
                  ></button>
                </div>
                <div class="glass-inset flex items-center gap-3 px-3 py-2">
                  <input
                    type="color"
                    v-model="formData.color"
                    class="w-8 h-8 rounded-md cursor-pointer p-0 border-none bg-transparent"
                  >
                  <span class="font-mono text-sm text-muted">{{ formData.color }}</span>
                </div>
              </div>
            </div>

            <div>
              <label class="label">Parent Project</label>
              <div ref="parentDropdownRef" class="relative cursor-pointer" @click="openParentDropdown">
                <div
                  v-if="!selectedParent"
                  class="input flex items-center gap-2.5 pr-9 text-fg-subtle"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="flex-shrink-0">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                  </svg>
                  <span>None (Root level)</span>
                </div>
                <div
                  v-else
                  class="input flex items-center gap-2.5 pr-9 text-fg"
                >
                  <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: selectedParent.color }"></div>
                  <span class="flex-1 truncate">{{ projectStore.getProjectPath(selectedParent.id) }}</span>
                  <button
                    type="button"
                    @click.stop="clearParent"
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
                    v-if="parentDropdownOpen"
                    class="glass-card absolute top-[calc(100%+6px)] left-0 right-0 z-50 overflow-hidden p-0"
                    @click.stop
                  >
                    <div class="flex items-center gap-2 px-3 py-2.5 border-b border-fg-subtle/15">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" class="text-fg-subtle flex-shrink-0">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                      </svg>
                      <input
                        v-model="parentSearchQuery"
                        class="parent-search-input flex-1 border-none outline-none text-sm bg-transparent text-fg placeholder:text-fg-subtle"
                        placeholder="Search projects..."
                        @click.stop
                      >
                    </div>
                    <div class="max-h-[200px] overflow-y-auto p-1.5">
                      <button
                        type="button"
                        :class="[
                          'glass-row w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-left',
                          !formData.parent_id ? 'text-accent font-semibold' : 'text-fg'
                        ]"
                        @click="selectParent(null)"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                        </svg>
                        <span>None (Root level)</span>
                      </button>
                      <button
                        v-for="p in parentOptions"
                        :key="p.id"
                        type="button"
                        :class="[
                          'glass-row w-full flex items-center gap-2.5 px-2.5 py-2 text-sm text-left',
                          formData.parent_id === p.id ? 'text-accent font-semibold' : 'text-fg'
                        ]"
                        @click="selectParent(p)"
                      >
                        <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: p.color }"></div>
                        <span class="flex-1 truncate">{{ projectStore.getProjectPath(p.id) }}</span>
                      </button>
                      <div v-if="parentOptions.length === 0" class="p-4 text-center text-sm text-subtle">
                        No projects found
                      </div>
                    </div>
                  </div>
                </Transition>
              </div>
            </div>
          </div>

          <div v-show="activeTab === 'settings'" class="flex flex-col gap-5">
            <div>
              <label class="label">Default Session Duration</label>
              <div class="flex items-center gap-3">
                <input
                  type="number"
                  v-model.number="formData.default_duration"
                  min="5"
                  class="input flex-1"
                >
                <span class="text-sm text-muted whitespace-nowrap">minutes</span>
              </div>
              <p class="text-xs text-subtle mt-1.5">Default time allocated when starting a session for this project</p>
            </div>

            <div>
              <label class="label">Notification Interval</label>
              <div class="flex items-center gap-3">
                <input
                  type="number"
                  v-model.number="formData.notification_interval"
                  min="1"
                  placeholder="Off"
                  class="input flex-1"
                >
                <span class="text-sm text-muted whitespace-nowrap">minutes</span>
              </div>
              <p class="text-xs text-subtle mt-1.5">Get reminded at this interval during sessions (leave empty to disable)</p>
            </div>

            <div>
              <label class="glass-inset flex items-center justify-between gap-3 px-4 py-3 cursor-pointer">
                <div class="flex flex-col gap-0.5">
                  <span class="text-sm font-medium text-fg">Pin this project</span>
                  <span class="text-xs text-subtle">Show at the top of your project list</span>
                </div>
                <div class="relative flex-shrink-0">
                  <input type="checkbox" v-model="formData.is_pinned" class="sr-only peer">
                  <span class="block w-11 h-6 bg-fg-subtle/40 peer-checked:bg-accent rounded-full transition-all duration-200"></span>
                  <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm transition-all duration-200 peer-checked:translate-x-5"></span>
                </div>
              </label>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-4 pt-4 border-t border-fg-subtle/15 flex-shrink-0">
          <button type="button" @click="emit('close')" class="btn btn-secondary">
            Cancel
          </button>
          <button type="submit" :disabled="saving || !formData.name" class="btn btn-primary">
            <svg
              v-if="saving"
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
            {{ saving ? 'Saving...' : (isEdit ? 'Save Changes' : 'Create Project') }}
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
