<script setup>
import { ref, computed } from 'vue'
import { useTagStore } from '@/stores/tags'
import { useProjectStore } from '@/stores/projects'

const props = defineProps({
  tag: Object  // null for create, object for edit
})

const emit = defineEmits(['close', 'saved'])

const tagStore = useTagStore()
const projectStore = useProjectStore()

const formData = ref({
  name: props.tag?.name || '',
  color: props.tag?.color || '#10B981',
  project_id: props.tag?.project_id || null
})

const isEdit = computed(() => !!props.tag)
const saving = ref(false)
const error = ref(null)

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
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="emit('close')">
    <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
      <h2 class="text-2xl font-bold mb-4">{{ isEdit ? 'Edit' : 'Create' }} Tag</h2>

      <div v-if="error" class="mb-4 p-3 bg-red-100 text-red-700 rounded">
        {{ error }}
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label class="block text-gray-700 font-medium mb-2">Name *</label>
          <input
            v-model="formData.name"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
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

        <div class="mb-6">
          <label class="block text-gray-700 font-medium mb-2">Scope</label>
          <select
            v-model="formData.project_id"
            class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option :value="null">Global (all projects)</option>
            <option
              v-for="p in projectStore.activeProjects"
              :key="p.id"
              :value="p.id"
            >
              {{ projectStore.getProjectPath(p.id) }}
            </option>
          </select>
          <p class="text-sm text-gray-500 mt-1">
            Global tags are available to all projects. Project-specific tags are only available to that project and its children.
          </p>
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
            class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
          >
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
