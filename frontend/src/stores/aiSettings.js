import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAISettingsStore = defineStore('aiSettings', {
  state: () => ({
    config: null,
    tools: [],
    loading: false,
    saving: false,
    error: null,
  }),

  actions: {
    async fetch() {
      this.loading = true
      this.error = null
      try {
        const [cfg, tools] = await Promise.all([
          api.get('/api/ai-settings/'),
          api.get('/api/ai-settings/tools'),
        ])
        this.config = cfg.data
        this.tools = tools.data
      } catch (err) {
        this.error = err.response?.data?.detail || err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async update(patch) {
      this.saving = true
      this.error = null
      try {
        const res = await api.put('/api/ai-settings/', patch)
        this.config = res.data
        return res.data
      } catch (err) {
        this.error = err.response?.data?.detail || err.message
        throw err
      } finally {
        this.saving = false
      }
    },
  },
})
