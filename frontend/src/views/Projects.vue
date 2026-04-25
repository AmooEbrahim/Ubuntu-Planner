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
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
      <div>
        <h1 class="page-title">Projects</h1>
        <p class="page-subtitle mt-1">Organize and manage your project hierarchy</p>
      </div>
      <button @click="openCreateForm" class="btn btn-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        New Project
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="glass-card p-5 flex items-center gap-4">
        <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-accent/15 text-accent flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <div class="flex flex-col min-w-0">
          <span class="text-2xl font-bold text-fg leading-tight">{{ stats.total }}</span>
          <span class="text-xs text-muted uppercase tracking-wide">Active</span>
        </div>
      </div>

      <div class="glass-card p-5 flex items-center gap-4">
        <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-warning/15 text-warning flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
          </svg>
        </div>
        <div class="flex flex-col min-w-0">
          <span class="text-2xl font-bold text-fg leading-tight">{{ stats.pinned }}</span>
          <span class="text-xs text-muted uppercase tracking-wide">Pinned</span>
        </div>
      </div>

      <div class="glass-card p-5 flex items-center gap-4">
        <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-info/15 text-info flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <polyline points="8 9 12 5 16 9"></polyline>
            <polyline points="8 15 12 19 16 15"></polyline>
          </svg>
        </div>
        <div class="flex flex-col min-w-0">
          <span class="text-2xl font-bold text-fg leading-tight">{{ stats.roots }}</span>
          <span class="text-xs text-muted uppercase tracking-wide">Root</span>
        </div>
      </div>

      <div v-if="stats.archived > 0" class="glass-card p-5 flex items-center gap-4">
        <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-fg-subtle/15 text-fg-muted flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <polyline points="21 8 21 21 3 21 3 8"></polyline>
            <rect x="1" y="3" width="22" height="5"></rect>
            <line x1="10" y1="12" x2="14" y2="12"></line>
          </svg>
        </div>
        <div class="flex flex-col min-w-0">
          <span class="text-2xl font-bold text-fg leading-tight">{{ stats.archived }}</span>
          <span class="text-xs text-muted uppercase tracking-wide">Archived</span>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="glass-card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 flex-wrap">
      <div class="relative flex-1 max-w-md">
        <svg
          class="absolute left-3.5 top-1/2 -translate-y-1/2 text-fg-subtle pointer-events-none"
          viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"
        >
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search projects..."
          class="input pl-10"
        >
      </div>

      <div class="flex items-center gap-3 flex-wrap">
        <div class="glass-inset flex p-1">
          <button
            :class="[
              'flex items-center justify-center w-9 h-9 rounded-lg transition-all duration-200',
              viewMode === 'grid'
                ? 'bg-accent/15 text-accent'
                : 'text-fg-muted hover:text-fg'
            ]"
            @click="viewMode = 'grid'"
            title="Grid view"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
            </svg>
          </button>
          <button
            :class="[
              'flex items-center justify-center w-9 h-9 rounded-lg transition-all duration-200',
              viewMode === 'tree'
                ? 'bg-accent/15 text-accent'
                : 'text-fg-muted hover:text-fg'
            ]"
            @click="viewMode = 'tree'"
            title="Tree view"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <polyline points="8 9 12 5 16 9"></polyline>
              <polyline points="8 15 12 19 16 15"></polyline>
            </svg>
          </button>
        </div>

        <label class="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            v-model="showArchived"
            @change="loadProjects"
            class="sr-only peer"
          >
          <span class="relative block w-10 h-[22px] bg-fg-subtle/40 peer-checked:bg-accent rounded-full transition-all duration-200">
            <span class="absolute top-[3px] left-[3px] w-4 h-4 bg-white rounded-full shadow-sm transition-transform duration-200 peer-checked:translate-x-[18px]"></span>
          </span>
          <span class="text-sm text-muted">Archived</span>
        </label>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="projectStore.loading" class="flex flex-col items-center justify-center py-16 gap-3 text-muted">
      <div class="spinner"></div>
      <p class="text-sm">Loading projects...</p>
    </div>

    <!-- Error -->
    <div
      v-else-if="projectStore.error"
      class="glass-card border-l-4 border-danger/60 bg-danger/5 text-danger flex items-center gap-2.5 px-4 py-3 text-sm"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="flex-shrink-0">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span class="flex-1">{{ projectStore.error }}</span>
    </div>

    <template v-else>
      <!-- Grid view -->
      <div v-if="viewMode === 'grid' && filteredTree.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <div
          v-for="project in filteredTree"
          :key="project.id"
          class="glass-card overflow-hidden transition-all duration-200 hover:-translate-y-0.5"
          :class="{ 'opacity-60': project.is_archived }"
        >
          <!-- Color accent strip -->
          <div class="h-1 w-full" :style="{ backgroundColor: project.color }"></div>
          <div class="p-5">
            <div class="mb-4">
              <div class="flex items-center gap-2.5 mb-1.5">
                <div class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: project.color }"></div>
                <h3 class="text-base font-semibold text-fg flex-1 truncate">{{ project.name }}</h3>
                <span
                  v-if="project.is_pinned"
                  class="badge badge-warning"
                  title="Pinned"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
                    <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
                  </svg>
                </span>
              </div>
              <p
                v-if="project.description"
                class="text-sm text-muted line-clamp-2"
              >{{ project.description }}</p>
            </div>

            <div class="flex gap-2 mb-4 flex-wrap">
              <span class="badge badge-neutral">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                {{ project.default_duration }}min
              </span>
              <span v-if="totalDescendants(project) > 0" class="badge badge-info">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                {{ totalDescendants(project) }} sub
              </span>
            </div>

            <div class="flex gap-1 pt-4 border-t border-fg-subtle/15">
              <button
                @click="handleStartSession(project)"
                class="icon-btn !text-success hover:!bg-success/15"
                title="Start session"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
              </button>
              <button
                @click="openEditForm(project)"
                class="icon-btn !text-accent hover:!bg-accent/15"
                title="Edit"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button
                @click="openCreateChildForm(project)"
                class="icon-btn !text-info hover:!bg-info/15"
                title="Add sub-project"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
              <button
                @click="handleTogglePin(project)"
                class="icon-btn !text-warning hover:!bg-warning/15"
                :title="project.is_pinned ? 'Unpin' : 'Pin'"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M16 12V4h1V2H7v2h1v8l-2 2v2h5.2v6h1.6v-6H18v-2l-2-2z"/>
                </svg>
              </button>
              <button
                @click="handleToggleArchive(project)"
                class="icon-btn"
                :title="project.is_archived ? 'Unarchive' : 'Archive'"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="21 8 21 21 3 21 3 8"></polyline>
                  <rect x="1" y="3" width="22" height="5"></rect>
                  <line x1="10" y1="12" x2="14" y2="12"></line>
                </svg>
              </button>
              <button
                @click="handleDelete(project)"
                class="icon-btn !text-danger hover:!bg-danger/15 ml-auto"
                title="Delete"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="totalDescendants(project) > 0" class="border-t border-fg-subtle/15">
            <button
              @click="toggleCardExpand(project.id)"
              class="flex items-center gap-2 w-full px-5 py-3 text-xs uppercase tracking-wide text-muted hover:bg-fg-subtle/10 transition-colors"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                width="14"
                height="14"
                class="transition-transform duration-200"
                :class="{ 'rotate-180': expandedCards.has(project.id) }"
              >
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
              <span>{{ totalDescendants(project) }} sub-project{{ totalDescendants(project) > 1 ? 's' : '' }}</span>
            </button>

            <Transition name="hierarchy">
              <div v-if="expandedCards.has(project.id)" class="flex flex-col pb-3">
                <div
                  v-for="item in flattenHierarchy(project).slice(1)"
                  :key="item.project.id"
                  class="relative flex items-center justify-between gap-2 py-1.5 pr-3 hover:bg-fg-subtle/5 transition-colors"
                  :style="{ paddingLeft: `${0.75 + item.depth * 1}rem` }"
                >
                  <div
                    v-if="item.depth > 0"
                    class="absolute top-[-0.25rem] bottom-0 w-px border-l-2 opacity-30"
                    :style="{ borderLeftColor: item.project.color, left: `${0.75 + (item.depth - 1) * 1}rem` }"
                  ></div>
                  <div
                    class="flex items-center gap-2 cursor-pointer flex-1 min-w-0"
                    @click="openEditForm(item.project)"
                  >
                    <div class="w-2 h-2 rounded-full flex-shrink-0" :style="{ backgroundColor: item.project.color }"></div>
                    <span class="text-sm text-fg truncate">{{ item.project.name }}</span>
                    <span
                      v-if="item.depth > 0"
                      class="text-[11px] text-subtle bg-fg-subtle/15 px-1.5 py-0.5 rounded flex-shrink-0"
                    >level {{ item.depth }}</span>
                  </div>
                  <button
                    @click="handleStartSession(item.project)"
                    class="flex items-center justify-center w-6 h-6 rounded-md text-success hover:bg-success/15 transition-colors flex-shrink-0"
                    title="Start session"
                  >
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

      <!-- Tree view -->
      <ProjectTree
        v-else-if="viewMode === 'tree' && filteredTree.length > 0"
        :projects="filteredTree"
        @edit="openEditForm"
        @delete="handleDelete"
        @toggle-archive="handleToggleArchive"
        @toggle-pin="handleTogglePin"
        @add-child="openCreateChildForm"
        @start-session="handleStartSession"
      />

      <!-- Empty state -->
      <div
        v-if="filteredTree.length === 0"
        class="glass-card flex flex-col items-center justify-center py-16 px-8 text-center"
      >
        <div class="flex items-center justify-center w-20 h-20 rounded-full bg-fg-subtle/15 text-fg-subtle mb-6">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="36" height="36">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <h3 v-if="searchQuery" class="text-lg font-semibold text-fg mb-2">No projects match "{{ searchQuery }}"</h3>
        <h3 v-else class="text-lg font-semibold text-fg mb-2">No projects yet</h3>
        <p v-if="!searchQuery" class="text-sm text-muted mb-5">Create your first project to get started planning your work.</p>
        <button v-if="!searchQuery" @click="openCreateForm" class="btn btn-primary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Create Project
        </button>
      </div>
    </template>

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
</style>
