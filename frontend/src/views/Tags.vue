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
const searchQuery = ref('')

const filteredTags = computed(() => {
  let tags
  if (!filterProject.value) tags = tagStore.tags
  else if (filterProject.value === 'global') tags = tagStore.globalTags
  else tags = tagStore.tagsByProject(filterProject.value)

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    tags = tags.filter(t => t.name.toLowerCase().includes(q))
  }
  return tags
})

const stats = computed(() => ({
  total: tagStore.tags.length,
  global: tagStore.globalTags.length,
  scoped: tagStore.tags.filter(t => t.project_id).length
}))

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

function getProjectColor(projectId) {
  if (!projectId) return '#818cf8'
  const project = projectStore.projects.find(p => p.id === projectId)
  return project ? project.color : '#94a3b8'
}
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <h1 class="page-title">Tags</h1>
        <p class="page-subtitle">Organize projects and sessions with color-coded labels</p>
      </div>
      <button @click="openCreateForm" class="btn btn-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        New Tag
      </button>
    </div>

    <div class="grid grid-cols-3 sm:flex sm:flex-row gap-3">
      <div class="glass-card p-4 flex items-center gap-3 flex-1">
        <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-accent/15 text-accent flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
            <line x1="7" y1="7" x2="7.01" y2="7"></line>
          </svg>
        </div>
        <div class="min-w-0">
          <div class="text-xl font-bold text-fg leading-none">{{ stats.total }}</div>
          <div class="text-xs text-muted uppercase tracking-wide mt-1">Total</div>
        </div>
      </div>
      <div class="glass-card p-4 flex items-center gap-3 flex-1">
        <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-info/15 text-info flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="2" y1="12" x2="22" y2="12"></line>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
          </svg>
        </div>
        <div class="min-w-0">
          <div class="text-xl font-bold text-fg leading-none">{{ stats.global }}</div>
          <div class="text-xs text-muted uppercase tracking-wide mt-1">Global</div>
        </div>
      </div>
      <div class="glass-card p-4 flex items-center gap-3 flex-1">
        <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-warning/15 text-warning flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <div class="min-w-0">
          <div class="text-xl font-bold text-fg leading-none">{{ stats.scoped }}</div>
          <div class="text-xs text-muted uppercase tracking-wide mt-1">Scoped</div>
        </div>
      </div>
    </div>

    <div class="glass-card p-3 flex items-center gap-3 flex-wrap">
      <div class="relative flex-1 min-w-[200px] max-w-md">
        <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 text-fg-subtle pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search tags..."
          class="input pl-10"
        >
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <button
          :class="[
            'btn btn-sm',
            filterProject === null ? 'btn-primary' : 'btn-secondary'
          ]"
          @click="filterProject = null"
        >
          All
        </button>
        <button
          :class="[
            'btn btn-sm',
            filterProject === 'global' ? 'btn-primary' : 'btn-secondary'
          ]"
          @click="filterProject = 'global'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="12" height="12">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="2" y1="12" x2="22" y2="12"></line>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
          </svg>
          Global
        </button>
        <select
          v-model="filterProject"
          class="input text-xs py-1.5 pr-8 max-w-[200px]"
        >
          <option :value="null" hidden>By project</option>
          <option
            v-for="p in projectStore.activeProjects"
            :key="p.id"
            :value="p.id"
          >
            {{ projectStore.getProjectPath(p.id) }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="tagStore.loading" class="glass-card flex flex-col items-center justify-center py-16 px-6 text-muted">
      <div class="spinner mb-4"></div>
      <p>Loading tags...</p>
    </div>

    <div v-else-if="tagStore.error" class="glass-card border-l-4 border-danger/60 bg-danger/5 flex flex-col items-center py-12 px-6 text-danger">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="40" height="40" class="mb-3">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <p>{{ tagStore.error }}</p>
    </div>

    <div v-else-if="filteredTags.length === 0" class="glass-card flex flex-col items-center justify-center py-16 px-6 text-center">
      <div class="flex items-center justify-center w-16 h-16 rounded-full bg-fg-subtle/15 text-fg-subtle mb-4">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" width="28" height="28">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
          <line x1="7" y1="7" x2="7.01" y2="7"></line>
        </svg>
      </div>
      <h3 v-if="searchQuery" class="text-base font-semibold text-fg mb-1">No tags match "{{ searchQuery }}"</h3>
      <h3 v-else class="text-base font-semibold text-fg mb-1">No tags yet</h3>
      <p v-if="!searchQuery" class="text-sm text-muted mb-4">Create your first tag to start organizing your projects.</p>
      <button v-if="!searchQuery" @click="openCreateForm" class="btn btn-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Create Tag
      </button>
    </div>

    <div v-else class="grid gap-4" style="grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));">
      <div
        v-for="tag in filteredTags"
        :key="tag.id"
        class="glass-card overflow-hidden transition-transform duration-200 hover:-translate-y-0.5"
      >
        <div class="h-1 w-full" :style="{ backgroundColor: tag.color }"></div>
        <div class="p-4 flex items-center gap-3">
          <div class="flex items-center justify-center w-10 h-10 rounded-xl flex-shrink-0 shadow-md" :style="{ backgroundColor: tag.color }">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
              <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
              <line x1="7" y1="7" x2="7.01" y2="7"></line>
            </svg>
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="font-semibold text-fg truncate">{{ tag.name }}</h3>
            <span class="inline-flex items-center gap-1 text-xs mt-0.5" :style="{ color: getProjectColor(tag.project_id) }">
              <svg v-if="!tag.project_id" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="12" height="12">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="12" height="12">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
              <span class="truncate">{{ getProjectName(tag.project_id) }}</span>
            </span>
          </div>
          <div class="flex gap-1 flex-shrink-0">
            <button @click="openEditForm(tag)" class="icon-btn !w-8 !h-8 hover:!text-accent hover:!bg-accent/15" title="Edit">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </button>
            <button @click="handleDelete(tag)" class="icon-btn !w-8 !h-8 hover:!text-danger hover:!bg-danger/15" title="Delete">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <Transition name="modal">
      <TagForm
        v-if="showForm"
        :tag="editingTag"
        @close="showForm = false"
        @saved="handleFormSaved"
      />
    </Transition>
  </div>
</template>
