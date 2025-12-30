<script setup>
import { ref, computed } from 'vue'
import { useProjectStore } from '@/stores/projects'

const props = defineProps({
  project: Object  // null for create, object for edit
})

const emit = defineEmits(['close', 'saved'])

const projectStore = useProjectStore()

const formData = ref({
  name: props.project?.name || '',
  parent_id: props.project?.parent_id || null,
  color: props.project?.color || '#3B82F6',
  description: props.project?.description || '',
  default_duration: props.project?.default_duration || 60,
  notification_interval: props.project?.notification_interval || null,
  is_pinned: props.project?.is_pinned || false
})

const isEdit = computed(() => !!props.project)
const saving = ref(false)
const error = ref(null)

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
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="emit('close')">
    <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
      <h2 class="text-2xl font-bold mb-4">{{ isEdit ? 'Edit' : 'Create' }} Project</h2>

      <div v-if="error" class="mb-4 p-3 bg-red-100 text-red-700 rounded">
        {{ error }}
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label class="block text-gray-700 font-medium mb-2">Name *</label>
          <input
            v-model="formData.name"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 font-medium mb-2">Color *</label>
          <input
            type="color"
            v-model="formData.color"
            required
            class="w-full h-10 border border-gray-300 rounded cursor-pointer"
          >
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 font-medium mb-2">Parent Project</label>
          <select
            v-model="formData.parent_id"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option :value="null">None (Root)</option>
            <option
              v-for="p in projectStore.activeProjects"
              :key="p.id"
              :value="p.id"
              :disabled="isEdit && p.id === project.id"
            >
              {{ projectStore.getProjectPath(p.id) }}
            </option>
          </select>
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 font-medium mb-2">Description</label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 font-medium mb-2">Default Duration (minutes)</label>
          <input
            type="number"
            v-model.number="formData.default_duration"
            min="5"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 font-medium mb-2">Notification Interval (minutes)</label>
          <input
            type="number"
            v-model.number="formData.notification_interval"
            min="1"
            placeholder="Optional"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
        </div>

        <div class="mb-6">
          <label class="flex items-center">
            <input type="checkbox" v-model="formData.is_pinned" class="mr-2">
            <span class="text-gray-700">Pin this project</span>
          </label>
        </div>

        <div class="flex justify-end gap-3">
          <button
            type="button"
            @click="emit('close')"
            class="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
