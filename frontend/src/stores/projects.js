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
