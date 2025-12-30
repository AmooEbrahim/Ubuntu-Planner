# Projects Frontend Implementation

Vue 3 frontend for project management.

## Store (Pinia)

Create `frontend/src/stores/projects.js`:

```javascript
import { defineStore } from 'pinia'
import api from '@/services/api'

export const useProjectStore = defineStore('projects', {
  state: () => ({
    projects: [],
    loading: false,
    error: null
  }),

  getters: {
    activeProjects: (state) => state.projects.filter(p => !p.is_archived),
    archivedProjects: (state) => state.projects.filter(p => p.is_archived),
    pinnedProjects: (state) => state.projects.filter(p => p.is_pinned && !p.is_archived),

    // Get project hierarchy as tree
    projectTree: (state) => {
      const buildTree = (parentId = null) => {
        return state.projects
          .filter(p => p.parent_id === parentId)
          .map(p => ({
            ...p,
            children: buildTree(p.id)
          }))
      }
      return buildTree()
    },

    // Get project with full path (Root > Parent > Child)
    getProjectPath: (state) => (projectId) => {
      const path = []
      let current = state.projects.find(p => p.id === projectId)

      while (current) {
        path.unshift(current.name)
        current = state.projects.find(p => p.id === current.parent_id)
      }

      return path.join(' > ')
    }
  },

  actions: {
    async fetchProjects(includeArchived = false) {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/api/projects/', {
          params: { include_archived: includeArchived }
        })
        this.projects = response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createProject(projectData) {
      const response = await api.post('/api/projects/', projectData)
      this.projects.push(response.data)
      return response.data
    },

    async updateProject(projectId, projectData) {
      const response = await api.put(`/api/projects/${projectId}`, projectData)
      const index = this.projects.findIndex(p => p.id === projectId)
      if (index !== -1) {
        this.projects[index] = response.data
      }
      return response.data
    },

    async deleteProject(projectId) {
      await api.delete(`/api/projects/${projectId}`)
      this.projects = this.projects.filter(p => p.id !== projectId)
    },

    async toggleArchive(projectId) {
      const project = this.projects.find(p => p.id === projectId)
      if (project) {
        await this.updateProject(projectId, { is_archived: !project.is_archived })
      }
    },

    async togglePin(projectId) {
      const project = this.projects.find(p => p.id === projectId)
      if (project) {
        await this.updateProject(projectId, { is_pinned: !project.is_pinned })
      }
    }
  }
})
```

## Projects Page

Create `frontend/src/views/Projects.vue`:

```vue
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
  await projectStore.fetchProjects(showArchived.value)
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
  if (confirm(`Delete project "${project.name}"?`)) {
    await projectStore.deleteProject(project.id)
  }
}

async function handleToggleArchive(project) {
  await projectStore.toggleArchive(project.id)
}

async function handleTogglePin(project) {
  await projectStore.togglePin(project.id)
}
</script>

<template>
  <div class="projects-page">
    <div class="header">
      <h1>Projects</h1>
      <div class="actions">
        <label>
          <input type="checkbox" v-model="showArchived" @change="loadProjects">
          Show archived
        </label>
        <button @click="openCreateForm" class="btn-primary">
          + New Project
        </button>
      </div>
    </div>

    <div v-if="projectStore.loading" class="loading">
      Loading projects...
    </div>

    <div v-else-if="projectStore.error" class="error">
      {{ projectStore.error }}
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
      @saved="showForm = false; loadProjects()"
    />
  </div>
</template>

<style scoped>
.projects-page {
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}
</style>
```

## Components

Create `frontend/src/components/ProjectForm.vue`:

```vue
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

async function handleSubmit() {
  try {
    if (isEdit.value) {
      await projectStore.updateProject(props.project.id, formData.value)
    } else {
      await projectStore.createProject(formData.value)
    }
    emit('saved')
  } catch (error) {
    alert('Error saving project: ' + error.message)
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <h2>{{ isEdit ? 'Edit' : 'Create' }} Project</h2>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Name *</label>
          <input v-model="formData.name" required>
        </div>

        <div class="form-group">
          <label>Color *</label>
          <input type="color" v-model="formData.color" required>
        </div>

        <div class="form-group">
          <label>Parent Project</label>
          <select v-model="formData.parent_id">
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

        <div class="form-group">
          <label>Default Duration (minutes)</label>
          <input type="number" v-model.number="formData.default_duration" min="5">
        </div>

        <div class="form-group">
          <label>
            <input type="checkbox" v-model="formData.is_pinned">
            Pin this project
          </label>
        </div>

        <div class="form-actions">
          <button type="button" @click="emit('close')">Cancel</button>
          <button type="submit" class="btn-primary">Save</button>
        </div>
      </form>
    </div>
  </div>
</template>
```

Create `frontend/src/components/ProjectTree.vue` for displaying hierarchical projects.

## Checklist

- [ ] Pinia store created with all actions
- [ ] Projects page created
- [ ] Project form component created
- [ ] Project tree component created
- [ ] Styling applied (Tailwind)
- [ ] Archive/unarchive works
- [ ] Pin/unpin works
- [ ] Create/edit/delete works
- [ ] Validation works
- [ ] Error handling works
