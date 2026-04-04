<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProjectStore } from '@/stores/projects'
import { useSessionStore } from '@/stores/sessions'
import ProjectForm from '@/components/ProjectForm.vue'
import ProjectTree from '@/components/ProjectTree.vue'

const projectStore = useProjectStore()
const sessionStore = useSessionStore()
const showForm = ref(false)
const editingProject = ref(null)
const parentProjectForNew = ref(null)
const showArchived = ref(false)
const searchQuery = ref('')
const viewMode = ref('grid')
const expandedCards = ref(new Set())

const projects = computed(() =>
  showArchived.value ? projectStore.projects : projectStore.activeProjects
)

const filteredTree = computed(() => {
  if (!searchQuery.value) return projectStore.projectTree
  const filterTree = (nodes) => {
    const q = searchQuery.value.toLowerCase()
    return nodes.reduce((acc, p) => {
      const matches = p.name.toLowerCase().includes(q) || (p.description && p.description.toLowerCase().includes(q))
      const filteredChildren = filterTree(p.children || [])
      if (matches || filteredChildren.length > 0) {
        acc.push({ ...p, children: filteredChildren })
      }
      return acc
    }, [])
  }
  return filterTree(projectStore.projectTree)
})

const stats = computed(() => ({
  total: projectStore.activeProjects.length,
  pinned: projectStore.pinnedProjects.length,
  archived: projectStore.archivedProjects.length,
  roots: projectStore.projectTree.length
}))

function flattenHierarchy(project, depth = 0) {
  const items = [{ project, depth }]
  const children = project.children || []
  for (const child of children) {
    items.push(...flattenHierarchy(child, depth + 1))
  }
  return items
}

function totalDescendants(project) {
  const children = project.children || []
  let count = children.length
  for (const child of children) {
    count += totalDescendants(child)
  }
  return count
}

function toggleCardExpand(projectId) {
  const set = new Set(expandedCards.value)
  if (set.has(projectId)) {
    set.delete(projectId)
  } else {
    set.add(projectId)
  }
  expandedCards.value = set
}

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
  parentProjectForNew.value = null
  showForm.value = true
}

function openEditForm(project) {
  editingProject.value = project
  parentProjectForNew.value = null
  showForm.value = true
}

function openCreateChildForm(project) {
  editingProject.value = null
  parentProjectForNew.value = project
  showForm.value = true
}

async function handleStartSession(project) {
  const activeSession = sessionStore.activeSession
  if (activeSession) {
    alert('You already have an active session. Please stop it before starting a new one.')
    return
  }
  try {
    await sessionStore.startSession({
      project_id: project.id,
      planned_duration: project.default_duration || 60,
      tag_ids: []
    })
  } catch (error) {
    alert('Failed to start session: ' + (error.response?.data?.detail || error.message))
  }
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
  <div class="projects-page">
    <div class="projects-header">
      <div class="header-top">
        <div>
          <h1 class="page-title">Projects</h1>
          <p class="page-subtitle">Organize and manage your project hierarchy</p>
        </div>
        <button @click="openCreateForm" class="btn-primary">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Project
        </button>
      </div>

      <div class="stats-row">
        <div class="stat-card">
          <span class="stat-value">{{ stats.total }}</span>
          <span class="stat-label">Active</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.pinned }}</span>
          <span class="stat-label">Pinned</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.roots }}</span>
          <span class="stat-label">Root</span>
        </div>
        <div class="stat-card" v-if="stats.archived > 0">
          <span class="stat-value">{{ stats.archived }}</span>
          <span class="stat-label">Archived</span>
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
            placeholder="Search projects..."
            class="search-input"
          >
        </div>

        <div class="toolbar-actions">
          <div class="view-toggle">
            <button
              :class="['view-btn', { active: viewMode === 'grid' }]"
              @click="viewMode = 'grid'"
              title="Grid view"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"></rect>
                <rect x="14" y="3" width="7" height="7"></rect>
                <rect x="3" y="14" width="7" height="7"></rect>
                <rect x="14" y="14" width="7" height="7"></rect>
              </svg>
            </button>
            <button
              :class="['view-btn', { active: viewMode === 'tree' }]"
              @click="viewMode = 'tree'"
              title="Tree view"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <polyline points="8 9 12 5 16 9"></polyline>
                <polyline points="8 15 12 19 16 15"></polyline>
              </svg>
            </button>
          </div>

          <label class="toggle-archived">
            <input type="checkbox" v-model="showArchived" @change="loadProjects">
            <span class="toggle-slider"></span>
            <span class="toggle-label">Archived</span>
          </label>
        </div>
      </div>
    </div>

    <div class="projects-content">
      <div v-if="projectStore.loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading projects...</p>
      </div>

      <div v-else-if="projectStore.error" class="error-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <p>{{ projectStore.error }}</p>
      </div>

      <template v-else>
        <div v-if="viewMode === 'grid'" class="projects-grid">
          <div
            v-for="project in filteredTree"
            :key="project.id"
            class="project-card"
            :class="{ 'is-pinned': project.is_pinned, 'is-archived': project.is_archived }"
          >
            <div class="card-accent" :style="{ backgroundColor: project.color }"></div>
            <div class="card-body">
              <div class="card-header">
                <div class="card-title-row">
                  <div class="card-color-dot" :style="{ backgroundColor: project.color }"></div>
                  <h3 class="card-title">{{ project.name }}</h3>
                  <button
                    v-if="project.is_pinned"
                    class="pin-badge"
                    title="Pinned"
                  >
                    <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
                      <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
                    </svg>
                  </button>
                </div>
                <p v-if="project.description" class="card-description">{{ project.description }}</p>
              </div>

              <div class="card-meta">
                <span class="meta-badge">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                  {{ project.default_duration }}min
                </span>
                <span v-if="totalDescendants(project) > 0" class="meta-badge">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                  </svg>
                  {{ totalDescendants(project) }} sub
                </span>
              </div>

              <div class="card-actions">
                <button @click="handleStartSession(project)" class="action-btn play" title="Start session">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                  </svg>
                </button>
                <button @click="openEditForm(project)" class="action-btn edit" title="Edit">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button @click="openCreateChildForm(project)" class="action-btn add" title="Add sub-project">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                </button>
                <button @click="handleTogglePin(project)" class="action-btn pin" :title="project.is_pinned ? 'Unpin' : 'Pin'">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
                  </svg>
                </button>
                <button @click="handleToggleArchive(project)" class="action-btn archive" :title="project.is_archived ? 'Unarchive' : 'Archive'">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <polyline points="21 8 21 21 3 21 3 8"></polyline>
                    <rect x="1" y="3" width="22" height="5"></rect>
                    <line x1="10" y1="12" x2="14" y2="12"></line>
                  </svg>
                </button>
                <button @click="handleDelete(project)" class="action-btn delete" title="Delete">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            </div>

            <div v-if="totalDescendants(project) > 0" class="card-hierarchy">
              <button @click="toggleCardExpand(project.id)" class="hierarchy-toggle">
                <svg
                  class="hierarchy-chevron"
                  :class="{ expanded: expandedCards.has(project.id) }"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  width="14"
                  height="14"
                >
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
                <span>{{ totalDescendants(project) }} sub-project{{ totalDescendants(project) > 1 ? 's' : '' }}</span>
              </button>

              <Transition name="hierarchy">
                <div v-if="expandedCards.has(project.id)" class="hierarchy-list">
                  <div
                    v-for="item in flattenHierarchy(project).slice(1)"
                    :key="item.project.id"
                    class="hierarchy-item"
                    :style="{ paddingLeft: `${0.75 + item.depth * 1}rem` }"
                  >
                    <div
                      class="hierarchy-line"
                      :style="{ borderLeftColor: item.project.color, left: `${0.75 + (item.depth - 1) * 1}rem` }"
                      v-if="item.depth > 0"
                    ></div>
                    <div class="hierarchy-info" @click="openEditForm(item.project)">
                      <div class="hierarchy-dot" :style="{ backgroundColor: item.project.color }"></div>
                      <span class="hierarchy-name">{{ item.project.name }}</span>
                      <span v-if="item.depth > 0" class="hierarchy-level">level {{ item.depth }}</span>
                    </div>
                    <button @click="handleStartSession(item.project)" class="hierarchy-play" title="Start session">
                      <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                      </svg>
                    </button>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>

        <ProjectTree
          v-else
          :projects="filteredTree"
          @edit="openEditForm"
          @delete="handleDelete"
          @toggle-archive="handleToggleArchive"
          @toggle-pin="handleTogglePin"
          @add-child="openCreateChildForm"
          @start-session="handleStartSession"
        />
      </template>

      <div v-if="!projectStore.loading && !projectStore.error && filteredTree.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <h3 v-if="searchQuery">No projects match "{{ searchQuery }}"</h3>
        <h3 v-else>No projects yet</h3>
        <p v-if="!searchQuery">Create your first project to get started planning your work.</p>
        <button v-if="!searchQuery" @click="openCreateForm" class="btn-primary mt-4">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Create Project
        </button>
      </div>
    </div>

    <Transition name="modal">
      <ProjectForm
        v-if="showForm"
        :project="editingProject"
        :parent-project="parentProjectForNew"
        @close="showForm = false"
        @saved="handleFormSaved"
      />
    </Transition>
  </div>
</template>

<style scoped>
.projects-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  --card-radius: 16px;
  --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-top {
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
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
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
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.search-input::placeholder {
  color: #94a3b8;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.view-toggle {
  display: flex;
  background: #f1f5f9;
  border-radius: 10px;
  padding: 3px;
}

.view-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
  transition: all var(--transition);
}

.view-btn svg {
  width: 18px;
  height: 18px;
}

.view-btn.active {
  background: white;
  color: #6366f1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toggle-archived {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
}

.toggle-archived input {
  display: none;
}

.toggle-slider {
  width: 40px;
  height: 22px;
  background: #cbd5e1;
  border-radius: 11px;
  position: relative;
  transition: all var(--transition);
}

.toggle-slider::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  top: 3px;
  left: 3px;
  transition: all var(--transition);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
}

.toggle-archived input:checked + .toggle-slider {
  background: #6366f1;
}

.toggle-archived input:checked + .toggle-slider::after {
  left: 21px;
}

.toggle-label {
  font-size: 0.85rem;
  color: #64748b;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.25rem;
}

.project-card {
  background: white;
  border-radius: var(--card-radius);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all var(--transition);
  position: relative;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.project-card.is-archived {
  opacity: 0.6;
}

.card-accent {
  height: 4px;
  width: 100%;
}

.card-body {
  padding: 1.25rem;
}

.card-header {
  margin-bottom: 1rem;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  margin-bottom: 0.375rem;
}

.card-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  flex: 1;
}

.pin-badge {
  display: flex;
  align-items: center;
  padding: 0.2rem 0.5rem;
  background: #fef3c7;
  border-radius: 6px;
  color: #d97706;
  border: none;
  cursor: default;
}

.card-description {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.meta-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.3rem 0.625rem;
  background: #f1f5f9;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #475569;
}

.card-actions {
  display: flex;
  gap: 0.375rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--transition);
}

.action-btn.play {
  background: #ecfdf5;
  color: #059669;
}

.action-btn.play:hover {
  background: #059669;
  color: white;
}

.action-btn.edit {
  color: #6366f1;
}

.action-btn.edit:hover {
  background: #6366f1;
  color: white;
}

.action-btn.add {
  color: #0ea5e9;
}

.action-btn.add:hover {
  background: #0ea5e9;
  color: white;
}

.action-btn.pin {
  color: #d97706;
}

.action-btn.pin:hover {
  background: #d97706;
  color: white;
}

.action-btn.archive {
  color: #64748b;
}

.action-btn.archive:hover {
  background: #64748b;
  color: white;
}

.action-btn.delete {
  color: #ef4444;
}

.action-btn.delete:hover {
  background: #ef4444;
  color: white;
}

.card-hierarchy {
  border-top: 1px solid #f1f5f9;
}

.hierarchy-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 1.25rem;
  border: none;
  background: transparent;
  font-size: 0.8rem;
  color: #64748b;
  cursor: pointer;
  transition: all var(--transition);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hierarchy-toggle:hover {
  background: #f8fafc;
  color: #334155;
}

.hierarchy-chevron {
  transition: transform var(--transition);
}

.hierarchy-chevron.expanded {
  transform: rotate(180deg);
}

.hierarchy-list {
  display: flex;
  flex-direction: column;
  padding: 0 0 0.75rem;
}

.hierarchy-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.75rem 0.4rem 1.25rem;
  transition: all var(--transition);
}

.hierarchy-item:hover {
  background: #f8fafc;
}

.hierarchy-line {
  position: absolute;
  top: -0.25rem;
  bottom: 0;
  width: 2px;
  border-left: 2px solid;
  opacity: 0.3;
}

.hierarchy-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  flex: 1;
  min-width: 0;
}

.hierarchy-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.hierarchy-name {
  font-size: 0.875rem;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hierarchy-level {
  font-size: 0.7rem;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  flex-shrink: 0;
}

.hierarchy-play {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  color: #059669;
  transition: all var(--transition);
  flex-shrink: 0;
}

.hierarchy-play:hover {
  background: #ecfdf5;
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
  border-top-color: #6366f1;
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

.error-state svg {
  width: 48px;
  height: 48px;
  color: #ef4444;
  margin-bottom: 1rem;
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

.hierarchy-enter-active,
.hierarchy-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.hierarchy-enter-from,
.hierarchy-leave-to {
  opacity: 0;
  max-height: 0;
}

@media (max-width: 768px) {
  .projects-page {
    padding: 1rem;
  }

  .header-top {
    flex-direction: column;
    gap: 1rem;
  }

  .stats-row {
    flex-wrap: wrap;
  }

  .stat-card {
    flex: 1;
    min-width: 80px;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    max-width: none;
  }

  .toolbar-actions {
    justify-content: space-between;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }
}
</style>
