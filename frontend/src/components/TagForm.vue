<script setup>
import { ref, computed } from 'vue'
import { useTagStore } from '@/stores/tags'
import { useProjectStore } from '@/stores/projects'

const props = defineProps({
  tag: Object
})

const emit = defineEmits(['close', 'saved'])

const tagStore = useTagStore()
const projectStore = useProjectStore()

const formData = ref({
  name: props.tag?.name || '',
  color: props.tag?.color || '#10b981',
  project_id: props.tag?.project_id || null
})

const isEdit = computed(() => !!props.tag)
const saving = ref(false)
const error = ref(null)

const presetColors = [
  '#10b981', '#059669', '#34d399', '#6ee7b7',
  '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
  '#ec4899', '#f43f5e', '#ef4444', '#f97316',
  '#f59e0b', '#eab308', '#84cc16', '#22c55e',
  '#14b8a6', '#06b6d4', '#0ea5e9', '#3b82f6'
]

const scopeOptions = computed(() => {
  return [
    { value: null, label: 'Global', description: 'Available to all projects', icon: 'globe' },
    ...projectStore.activeProjects.map(p => ({
      value: p.id,
      label: projectStore.getProjectPath(p.id),
      description: `Only for ${p.name} and children`,
      icon: 'folder',
      color: p.color
    }))
  ]
})

async function handleSubmit() {
  saving.value = true
  error.value = null
  try {
    if (isEdit.value) {
      await tagStore.updateTag(props.tag.id, formData.value)
    } else {
      await tagStore.createTag(formData.value)
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
          <div class="header-icon" :style="{ backgroundColor: isEdit ? '#f1f5f9' : '#ecfdf5' }">
            <svg v-if="isEdit" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" width="20" height="20">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" width="20" height="20">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </div>
          <div>
            <h2 class="modal-title">{{ isEdit ? 'Edit Tag' : 'Create Tag' }}</h2>
            <p class="modal-subtitle">{{ isEdit ? 'Update tag properties' : 'Add a new label for organizing' }}</p>
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

      <form @submit.prevent="handleSubmit" class="modal-form">
        <div class="form-group">
          <label class="form-label">Tag Name</label>
          <input
            v-model="formData.name"
            required
            placeholder="e.g., Backend, Urgent, Research"
            class="form-input"
          >
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
          <label class="form-label">Scope</label>
          <div class="scope-list">
            <button
              v-for="option in scopeOptions"
              :key="option.value"
              type="button"
              :class="['scope-option', { active: formData.project_id === option.value }]"
              @click="formData.project_id = option.value"
            >
              <div class="scope-icon" :style="option.color ? { color: option.color } : {}">
                <svg v-if="option.icon === 'globe'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <div class="scope-text">
                <span class="scope-label">{{ option.label }}</span>
                <span class="scope-desc">{{ option.description }}</span>
              </div>
              <div :class="['scope-radio', { checked: formData.project_id === option.value }]">
                <div v-if="formData.project_id === option.value" class="scope-radio-dot"></div>
              </div>
            </button>
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
            {{ saving ? 'Saving...' : (isEdit ? 'Save Changes' : 'Create Tag') }}
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
  max-width: 480px;
  height: 520px;
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

.modal-form {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 0 1.5rem 1.5rem;
  gap: 1.25rem;
  overflow-y: auto;
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
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-input::placeholder {
  color: #94a3b8;
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

.scope-list {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  max-height: 200px;
  overflow-y: auto;
}

.scope-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.scope-option:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.scope-option.active {
  border-color: #10b981;
  background: #ecfdf5;
}

.scope-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f1f5f9;
  border-radius: 8px;
  color: #64748b;
  flex-shrink: 0;
}

.scope-option.active .scope-icon {
  background: white;
}

.scope-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.scope-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.scope-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.scope-radio {
  width: 20px;
  height: 20px;
  border: 2px solid #cbd5e1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.scope-option.active .scope-radio {
  border-color: #10b981;
  background: #10b981;
}

.scope-radio-dot {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: auto;
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
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
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
