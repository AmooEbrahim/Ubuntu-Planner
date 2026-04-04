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
  if (!projectId) return '#6366f1'
  const project = projectStore.projects.find(p => p.id === projectId)
  return project ? project.color : '#94a3b8'
}
</script>

<template>
  <div class="tags-page">
    <div class="tags-header">
      <div>
        <h1 class="page-title">Tags</h1>
        <p class="page-subtitle">Organize projects and sessions with color-coded labels</p>
      </div>
      <button @click="openCreateForm" class="btn-primary">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        New Tag
      </button>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-value">{{ stats.total }}</span>
        <span class="stat-label">Total</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.global }}</span>
        <span class="stat-label">Global</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.scoped }}</span>
        <span class="stat-label">Scoped</span>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search tags..."
          class="search-input"
        >
      </div>

      <div class="filter-group">
        <button
          :class="['filter-chip', { active: filterProject === null }]"
          @click="filterProject = null"
        >
          All
        </button>
        <button
          :class="['filter-chip', { active: filterProject === 'global' }]"
          @click="filterProject = 'global'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="2" y1="12" x2="22" y2="12"></line>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
          </svg>
          Global
        </button>
        <select
          v-model="filterProject"
          class="project-filter"
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

    <div v-if="tagStore.loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading tags...</p>
    </div>

    <div v-else-if="tagStore.error" class="error-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <p>{{ tagStore.error }}</p>
    </div>

    <div v-else-if="filteredTags.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
          <line x1="7" y1="7" x2="7.01" y2="7"></line>
        </svg>
      </div>
      <h3 v-if="searchQuery">No tags match "{{ searchQuery }}"</h3>
      <h3 v-else>No tags yet</h3>
      <p v-if="!searchQuery">Create your first tag to start organizing your projects.</p>
      <button v-if="!searchQuery" @click="openCreateForm" class="btn-primary mt-4">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Create Tag
      </button>
    </div>

    <div v-else class="tags-grid">
      <div
        v-for="tag in filteredTags"
        :key="tag.id"
        class="tag-card"
      >
        <div class="tag-color-bar" :style="{ backgroundColor: tag.color }"></div>
        <div class="tag-card-body">
          <div class="tag-card-top">
            <div class="tag-preview" :style="{ backgroundColor: tag.color }">
              <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" width="16" height="16">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                <line x1="7" y1="7" x2="7.01" y2="7"></line>
              </svg>
            </div>
            <div class="tag-info">
              <h3 class="tag-name">{{ tag.name }}</h3>
              <span class="tag-scope" :style="{ color: getProjectColor(tag.project_id) }">
                <svg v-if="!tag.project_id" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="2" y1="12" x2="22" y2="12"></line>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                {{ getProjectName(tag.project_id) }}
              </span>
            </div>
          </div>
          <div class="tag-card-actions">
            <button @click="openEditForm(tag)" class="tag-action-btn edit" title="Edit">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </button>
            <button @click="handleDelete(tag)" class="tag-action-btn delete" title="Delete">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
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

<style scoped>
.tags-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.025em;
}

.page-subtitle {
  color: #64748b;
  margin: 0.25rem 0 0;
  font-size: 0.95rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.icon {
  width: 18px;
  height: 18px;
}

.stats-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 1.5rem;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  min-width: 100px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.125rem;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #94a3b8;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.95rem;
  background: white;
  color: #0f172a;
  transition: all var(--transition);
}

.search-input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.search-input::placeholder {
  color: #94a3b8;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #64748b;
  cursor: pointer;
  transition: all var(--transition);
}

.filter-chip:hover {
  border-color: #10b981;
  color: #10b981;
}

.filter-chip.active {
  background: #ecfdf5;
  border-color: #10b981;
  color: #059669;
}

.project-filter {
  padding: 0.5rem 2rem 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #64748b;
  background: white;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  transition: all var(--transition);
}

.project-filter:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.tag-card {
  background: white;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all var(--transition);
}

.tag-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
  border-color: transparent;
}

.tag-color-bar {
  height: 3px;
  width: 100%;
}

.tag-card-body {
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.tag-card-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.tag-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  flex-shrink: 0;
}

.tag-info {
  min-width: 0;
  flex: 1;
}

.tag-name {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tag-scope {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  margin-top: 0.125rem;
}

.tag-card-actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.tag-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--transition);
}

.tag-action-btn.edit {
  color: #6366f1;
}

.tag-action-btn.edit:hover {
  background: #6366f1;
  color: white;
}

.tag-action-btn.delete {
  color: #ef4444;
}

.tag-action-btn.delete:hover {
  background: #ef4444;
  color: white;
}

.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p, .error-state p {
  color: #64748b;
  font-size: 0.95rem;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.empty-icon svg {
  width: 36px;
  height: 36px;
  color: #94a3b8;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 0.5rem;
}

.empty-state p {
  color: #64748b;
  margin: 0;
}

.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .tags-page {
    padding: 1rem;
  }

  .tags-header {
    flex-direction: column;
    gap: 1rem;
  }

  .stats-row {
    flex-wrap: wrap;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    max-width: none;
  }

  .filter-group {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .tags-grid {
    grid-template-columns: 1fr;
  }
}
</style>
