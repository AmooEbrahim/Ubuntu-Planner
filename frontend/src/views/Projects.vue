<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProjectStore } from '@/stores/projects'
import ProjectForm from '@/components/ProjectForm.vue'
import ProjectTree from '@/components/ProjectTree.vue'

const projectStore = useProjectStore()
const showForm = ref(false)
const editingProject = ref(null)
const showArchived = ref(false)

const projects = computed(() =>
  showArchived.value ? projectStore.projects : projectStore.activeProjects
)

onMounted(() => {
  loadProjects()
})

async function loadProjects() {
  try {
    await projectStore.fetchProjects(showArchived.value)
  } catch (error) {
    console.error('Failed to load projects:', error)
  }
}

function openCreateForm() {
  editingProject.value = null
  showForm.value = true
}

function openEditForm(project) {
  editingProject.value = project
  showForm.value = true
}

async function handleDelete(project) {
  if (confirm(`Delete project "${project.name}"? This will also delete all child projects, planning entries, and sessions.`)) {
    try {
      await projectStore.deleteProject(project.id)
    } catch (error) {
      alert('Failed to delete project: ' + (error.response?.data?.detail || error.message))
    }
  }
}

async function handleToggleArchive(project) {
  try {
    await projectStore.toggleArchive(project.id)
  } catch (error) {
    alert('Failed to toggle archive: ' + (error.response?.data?.detail || error.message))
  }
}

async function handleTogglePin(project) {
  try {
    await projectStore.togglePin(project.id)
  } catch (error) {
    alert('Failed to toggle pin: ' + (error.response?.data?.detail || error.message))
  }
}

function handleFormSaved() {
  showForm.value = false
  loadProjects()
}
</script>

<template>
  <div class="projects-page max-w-6xl mx-auto p-6">
    <div class="header flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-800">Projects</h1>
      <div class="flex items-center gap-4">
        <label class="flex items-center text-gray-700">
          <input
            type="checkbox"
            v-model="showArchived"
            @change="loadProjects"
            class="mr-2"
          >
          Show archived
        </label>
        <button
          @click="openCreateForm"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          + New Project
        </button>
      </div>
    </div>

    <div v-if="projectStore.loading" class="text-center py-8 text-gray-500">
      Loading projects...
    </div>

    <div v-else-if="projectStore.error" class="text-center py-8 text-red-600">
      Error: {{ projectStore.error }}
    </div>

    <ProjectTree
      v-else
      :projects="projectStore.projectTree"
      @edit="openEditForm"
      @delete="handleDelete"
      @toggle-archive="handleToggleArchive"
      @toggle-pin="handleTogglePin"
    />

    <ProjectForm
      v-if="showForm"
      :project="editingProject"
      @close="showForm = false"
      @saved="handleFormSaved"
    />
  </div>
</template>
