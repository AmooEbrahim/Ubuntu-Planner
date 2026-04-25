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
    <div class="glass-panel w-full max-w-lg max-h-[90vh] flex flex-col">
      <div class="flex justify-between items-center p-6 pb-4 flex-shrink-0">
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-accent/15 text-accent">
            <svg v-if="isEdit" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </div>
          <div>
            <h2 class="text-lg font-bold text-fg">{{ isEdit ? 'Edit Tag' : 'Create Tag' }}</h2>
            <p class="text-xs text-muted mt-0.5">{{ isEdit ? 'Update tag properties' : 'Add a new label for organizing' }}</p>
          </div>
        </div>
        <button @click="emit('close')" class="icon-btn" title="Close">
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

      <form @submit.prevent="handleSubmit" class="flex flex-col flex-1 min-h-0 px-6 pb-6 gap-5 overflow-y-auto">
        <div>
          <label class="label">Tag Name</label>
          <input
            v-model="formData.name"
            required
            placeholder="e.g., Backend, Urgent, Research"
            class="input"
          >
        </div>

        <div>
          <label class="label">Color</label>
          <div class="flex flex-col gap-3">
            <div class="grid gap-2" style="grid-template-columns: repeat(10, 1fr);">
              <button
                v-for="color in presetColors"
                :key="color"
                type="button"
                class="aspect-square rounded-lg transition-all duration-150 hover:scale-110 focus:outline-none"
                :class="formData.color === color ? 'ring-2 ring-offset-2 ring-fg ring-offset-transparent' : ''"
                :style="{ backgroundColor: color }"
                @click="formData.color = color"
                :aria-label="color"
              ></button>
            </div>
            <div class="flex items-center gap-3 px-3 py-2 rounded-xl glass-inset">
              <input
                type="color"
                v-model="formData.color"
                class="w-8 h-8 rounded-md cursor-pointer p-0 border-0 bg-transparent"
                aria-label="Custom color"
              >
              <span class="font-mono text-sm text-muted">{{ formData.color }}</span>
            </div>
          </div>
        </div>

        <div>
          <label class="label">Scope</label>
          <div class="flex flex-col gap-1.5 max-h-52 overflow-y-auto">
            <button
              v-for="option in scopeOptions"
              :key="option.value"
              type="button"
              class="flex items-center gap-3 px-3 py-2.5 rounded-xl border transition-all duration-150 text-left"
              :class="formData.project_id === option.value
                ? 'border-accent/50 bg-accent/10'
                : 'border-fg-subtle/15 bg-transparent hover:bg-fg-subtle/5'"
              @click="formData.project_id = option.value"
            >
              <div
                class="flex items-center justify-center w-8 h-8 rounded-lg flex-shrink-0"
                :class="formData.project_id === option.value ? 'bg-white/40 dark:bg-white/10' : 'bg-fg-subtle/15'"
                :style="option.color ? { color: option.color } : { color: 'rgb(var(--fg-muted))' }"
              >
                <svg v-if="option.icon === 'globe'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <div class="flex-1 min-w-0 flex flex-col">
                <span class="text-sm font-medium text-fg truncate">{{ option.label }}</span>
                <span class="text-xs text-subtle truncate">{{ option.description }}</span>
              </div>
              <div
                class="w-5 h-5 border-2 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-150"
                :class="formData.project_id === option.value ? 'border-accent bg-accent' : 'border-fg-subtle/40'"
              >
                <div v-if="formData.project_id === option.value" class="w-1.5 h-1.5 bg-white rounded-full"></div>
              </div>
            </button>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-auto pt-4 border-t border-fg-subtle/15 flex-shrink-0">
          <button type="button" @click="emit('close')" class="btn btn-secondary">
            Cancel
          </button>
          <button type="submit" :disabled="saving || !formData.name" class="btn btn-primary">
            <svg v-if="saving" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="animate-spin">
              <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="10"></circle>
            </svg>
            {{ saving ? 'Saving...' : (isEdit ? 'Save Changes' : 'Create Tag') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
