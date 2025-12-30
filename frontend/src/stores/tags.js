import { defineStore } from 'pinia'
import api from '@/services/api'

export const useTagStore = defineStore('tags', {
  state: () => ({
    tags: [],
    loading: false,
    error: null
  }),

  getters: {
    globalTags: (state) => state.tags.filter(t => t.project_id === null),
    projectTags: (state) => state.tags.filter(t => t.project_id !== null),

    tagsByProject: (state) => (projectId) => {
      return state.tags.filter(t => t.project_id === projectId)
    }
  },

  actions: {
    async fetchTags() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/api/tags/')
        this.tags = response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTagsForProject(projectId) {
      const response = await api.get(`/api/tags/project/${projectId}`)
      return response.data
    },

    async createTag(tagData) {
      const response = await api.post('/api/tags/', tagData)
      this.tags.push(response.data)
      return response.data
    },

    async updateTag(tagId, tagData) {
      const response = await api.put(`/api/tags/${tagId}`, tagData)
      const index = this.tags.findIndex(t => t.id === tagId)
      if (index !== -1) {
        this.tags[index] = response.data
      }
      return response.data
    },

    async deleteTag(tagId) {
      await api.delete(`/api/tags/${tagId}`)
      this.tags = this.tags.filter(t => t.id !== tagId)
    }
  }
})
