import { defineStore } from 'pinia'
import api from '@/services/api'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    settings: {}
  }),

  actions: {
    async getAll() {
      const response = await api.get('/api/settings')
      this.settings = response.data
      return this.settings
    },

    async get(key) {
      const response = await api.get(`/api/settings/${key}`)
      return response.data
    },

    async update(key, value) {
      const response = await api.put(`/api/settings/${key}`, value)
      this.settings[key] = value
      return response.data
    },

    async updateMultiple(updates) {
      const response = await api.post('/api/settings/bulk-update', {
        settings: updates
      })
      Object.assign(this.settings, updates)
      return response.data
    },

    async getAvailableSounds() {
      const response = await api.get('/api/settings/sounds/available')
      return response.data
    }
  }
})
