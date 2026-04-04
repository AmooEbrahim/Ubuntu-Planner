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
    <div class="modal-container">
      <div class="modal-header">
        <div class="header-content">
          <div class="header-icon" :style="{ backgroundColor: isEdit ? '#f1f5f9' : '#eef2ff' }">
            <svg v-if="isEdit" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" width="20" height="20">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2" width="20" height="20">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </div>
          <div>
            <h2 class="modal-title">{{ isEdit ? 'Edit Project' : 'Create Project' }}</h2>
            <p class="modal-subtitle">{{ isEdit ? 'Update project settings' : 'Set up a new project to track' }}</p>
          </div>
        </div>
        <button @click="emit('close')" class="close-btn" title="Close">
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

      <div class="modal-tabs">
        <button
          :class="['tab-btn', { active: activeTab === 'details' }]"
          @click="activeTab = 'details'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          Details
        </button>
        <button
          :class="['tab-btn', { active: activeTab === 'settings' }]"
          @click="activeTab = 'settings'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          Settings
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-form">
        <div class="tab-content-wrapper">
          <div v-show="activeTab === 'details'" class="tab-content">
            <div class="form-group">
              <label class="form-label">Project Name</label>
              <input
                v-model="formData.name"
                required
                placeholder="e.g., Website Redesign"
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea
                v-model="formData.description"
                rows="3"
                placeholder="What is this project about?"
                class="form-input form-textarea"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Color</label>
              <div class="color-picker">
                <div class="color-grid">
                  <button
                    v-for="color in presetColors"
                    :key="color"
                    type="button"
                    :class="['color-swatch', { active: formData.color === color }]"
                    :style="{ backgroundColor: color }"
                    @click="formData.color = color"
                  ></button>
                </div>
                <div class="color-custom">
                  <input
                    type="color"
                    v-model="formData.color"
                    class="color-input"
                  >
                  <span class="color-hex">{{ formData.color }}</span>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Parent Project</label>
              <div ref="parentDropdownRef" class="parent-select" @click="openParentDropdown">
                <div v-if="!selectedParent" class="parent-placeholder">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                  </svg>
                  <span>None (Root level)</span>
                </div>
                <div v-else class="parent-selected">
                  <div class="parent-dot" :style="{ backgroundColor: selectedParent.color }"></div>
                  <span class="parent-name">{{ projectStore.getProjectPath(selectedParent.id) }}</span>
                  <button type="button" @click.stop="clearParent" class="parent-clear" title="Clear">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </div>
                <svg class="parent-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>

                <Transition name="dropdown">
                  <div v-if="parentDropdownOpen" class="parent-dropdown" @click.stop>
                    <div class="parent-search">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                      </svg>
                      <input
                        v-model="parentSearchQuery"
                        class="parent-search-input"
                        placeholder="Search projects..."
                        @click.stop
                      >
                    </div>
                    <div class="parent-list">
                      <button
                        type="button"
                        :class="['parent-option', { active: !formData.parent_id }]"
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
                        :class="['parent-option', { active: formData.parent_id === p.id }]"
                        @click="selectParent(p)"
                      >
                        <div class="parent-dot" :style="{ backgroundColor: p.color }"></div>
                        <span class="parent-option-path">{{ projectStore.getProjectPath(p.id) }}</span>
                      </button>
                      <div v-if="parentOptions.length === 0" class="parent-empty">
                        No projects found
                      </div>
                    </div>
                  </div>
                </Transition>
              </div>
            </div>
          </div>

          <div v-show="activeTab === 'settings'" class="tab-content">
            <div class="form-group">
              <label class="form-label">Default Session Duration</label>
              <div class="input-with-unit">
                <input
                  type="number"
                  v-model.number="formData.default_duration"
                  min="5"
                  class="form-input"
                >
                <span class="unit">minutes</span>
              </div>
              <p class="form-hint">Default time allocated when starting a session for this project</p>
            </div>

            <div class="form-group">
              <label class="form-label">Notification Interval</label>
              <div class="input-with-unit">
                <input
                  type="number"
                  v-model.number="formData.notification_interval"
                  min="1"
                  placeholder="Off"
                  class="form-input"
                >
                <span class="unit">minutes</span>
              </div>
              <p class="form-hint">Get reminded at this interval during sessions (leave empty to disable)</p>
            </div>

            <div class="form-group">
              <label class="form-toggle">
                <div class="toggle-content">
                  <span class="form-label">Pin this project</span>
                  <span class="form-hint">Show at the top of your project list</span>
                </div>
                <div class="toggle-wrapper">
                  <input type="checkbox" v-model="formData.is_pinned" class="toggle-input">
                  <span class="toggle-slider"></span>
                </div>
              </label>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" @click="emit('close')" class="btn-secondary">
            Cancel
          </button>
          <button type="submit" :disabled="saving || !formData.name" class="btn-primary">
            <svg v-if="saving" class="btn-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
  height: 580px;
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

.modal-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 1rem 1.5rem 0;
  background: #f8fafc;
  margin: 0 1.5rem;
  border-radius: 10px;
  flex-shrink: 0;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  padding: 0.625rem 1rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: white;
  color: #6366f1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.tab-btn:hover:not(.active) {
  color: #334155;
}

.modal-form {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 0 1.5rem 1.5rem;
}

.tab-content-wrapper {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-top: 1.25rem;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #0f172a;
  background: white;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input::placeholder {
  color: #94a3b8;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
}

.color-picker {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 0.5rem;
}

.color-swatch {
  aspect-ratio: 1;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
}

.color-swatch:hover {
  transform: scale(1.1);
}

.color-swatch.active {
  border-color: #0f172a;
  box-shadow: 0 0 0 2px white, 0 0 0 4px #0f172a;
}

.color-custom {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.color-input {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  padding: 0;
  background: none;
}

.color-input::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color-input::-webkit-color-swatch {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

.color-hex {
  font-family: monospace;
  font-size: 0.875rem;
  color: #64748b;
}

.parent-select {
  position: relative;
  cursor: pointer;
}

.parent-placeholder,
.parent-selected {
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

.parent-placeholder {
  color: #94a3b8;
}

.parent-select:hover .parent-placeholder,
.parent-select:hover .parent-selected {
  border-color: #cbd5e1;
}

.parent-select:focus-within .parent-placeholder,
.parent-select:focus-within .parent-selected {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.parent-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.parent-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.parent-clear {
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

.parent-clear:hover {
  background: #f1f5f9;
  color: #64748b;
}

.parent-chevron {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #94a3b8;
  pointer-events: none;
}

.parent-dropdown {
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

.parent-search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.parent-search svg {
  color: #94a3b8;
  flex-shrink: 0;
}

.parent-search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.875rem;
  color: #0f172a;
  background: transparent;
}

.parent-search-input::placeholder {
  color: #94a3b8;
}

.parent-list {
  max-height: 200px;
  overflow-y: auto;
  padding: 0.375rem;
}

.parent-option {
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

.parent-option:hover {
  background: #f8fafc;
}

.parent-option.active {
  background: #eef2ff;
  color: #6366f1;
}

.parent-option-path {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.parent-empty {
  padding: 1rem;
  text-align: center;
  font-size: 0.85rem;
  color: #94a3b8;
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.input-with-unit .form-input {
  flex: 1;
}

.unit {
  font-size: 0.875rem;
  color: #64748b;
  white-space: nowrap;
}

.form-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-radius: 10px;
  cursor: pointer;
}

.toggle-content {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.toggle-wrapper {
  position: relative;
  flex-shrink: 0;
}

.toggle-input {
  display: none;
}

.toggle-slider {
  display: block;
  width: 44px;
  height: 24px;
  background: #cbd5e1;
  border-radius: 12px;
  position: relative;
  transition: all 0.2s ease;
}

.toggle-slider::after {
  content: '';
  position: absolute;
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  top: 3px;
  left: 3px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.toggle-input:checked + .toggle-slider {
  background: #6366f1;
}

.toggle-input:checked + .toggle-slider::after {
  left: 23px;
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

  .color-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
