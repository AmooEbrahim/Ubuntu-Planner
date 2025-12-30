<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTagStore } from '@/stores/tags'
import { useProjectStore } from '@/stores/projects'
import TagForm from '@/components/TagForm.vue'

const tagStore = useTagStore()
const projectStore = useProjectStore()
const showForm = ref(false)
const editingTag = ref(null)
const filterProject = ref(null)

const filteredTags = computed(() => {
  if (!filterProject.value) return tagStore.tags

  if (filterProject.value === 'global') {
    return tagStore.globalTags
  }

  return tagStore.tagsByProject(filterProject.value)
})

onMounted(async () => {
  await loadData()
})

async function loadData() {
  try {
    await Promise.all([
      tagStore.fetchTags(),
      projectStore.fetchProjects()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

function openCreateForm() {
  editingTag.value = null
  showForm.value = true
}

function openEditForm(tag) {
  editingTag.value = tag
  showForm.value = true
}

async function handleDelete(tag) {
  if (confirm(`Delete tag "${tag.name}"?`)) {
    try {
      await tagStore.deleteTag(tag.id)
    } catch (error) {
      alert('Failed to delete tag: ' + (error.response?.data?.detail || error.message))
    }
  }
}

function handleFormSaved() {
  showForm.value = false
  tagStore.fetchTags()
}

function getProjectName(projectId) {
  if (!projectId) return 'Global'
  const project = projectStore.projects.find(p => p.id === projectId)
  return project ? projectStore.getProjectPath(projectId) : 'Unknown Project'
}
</script>

<template>
  <div class="tags-page max-w-6xl mx-auto p-6">
    <div class="header flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-800">Tags</h1>
      <div class="flex items-center gap-4">
        <select
          v-model="filterProject"
          class="px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <option :value="null">All Tags</option>
          <option value="global">Global Tags Only</option>
          <option v-for="p in projectStore.activeProjects" :key="p.id" :value="p.id">
            {{ projectStore.getProjectPath(p.id) }}
          </option>
        </select>
        <button
          @click="openCreateForm"
          class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          + New Tag
        </button>
      </div>
    </div>

    <div v-if="tagStore.loading" class="text-center py-8 text-gray-500">
      Loading tags...
    </div>

    <div v-else-if="tagStore.error" class="text-center py-8 text-red-600">
      Error: {{ tagStore.error }}
    </div>

    <div v-else-if="filteredTags.length === 0" class="text-center py-8 text-gray-500">
      No tags found. Create your first tag to get started.
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="tag in filteredTags"
        :key="tag.id"
        class="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between mb-2">
          <div
            class="px-3 py-1 rounded text-white font-medium"
            :style="{ backgroundColor: tag.color }"
          >
            {{ tag.name }}
          </div>
          <span class="text-sm text-gray-500">
            {{ getProjectName(tag.project_id) }}
          </span>
        </div>

        <div class="flex justify-end gap-2 mt-3">
          <button
            @click="openEditForm(tag)"
            class="text-sm px-3 py-1 text-blue-600 hover:text-blue-800"
          >
            Edit
          </button>
          <button
            @click="handleDelete(tag)"
            class="text-sm px-3 py-1 text-red-600 hover:text-red-800"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <TagForm
      v-if="showForm"
      :tag="editingTag"
      @close="showForm = false"
      @saved="handleFormSaved"
    />
  </div>
</template>
