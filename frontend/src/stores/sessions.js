import { defineStore } from 'pinia'
import api from '@/services/api'

export const useSessionStore = defineStore('sessions', {
  state: () => ({
    activeSession: null,
    recentSessions: [],
    loading: false,
    error: null,
    pollInterval: null,
  }),

  getters: {
    isSessionActive: (state) => state.activeSession !== null,

    elapsedMinutes: (state) => {
      if (!state.activeSession) return 0
      const start = new Date(state.activeSession.start_time)
      const now = new Date()
      return Math.floor((now - start) / 1000 / 60)
    },

    remainingMinutes: (state) => {
      if (!state.activeSession) return 0
      const elapsed = state.elapsedMinutes
      return Math.max(0, state.activeSession.planned_duration - elapsed)
    },

    isOvertime: (state) => {
      if (!state.activeSession) return false
      return state.elapsedMinutes > state.activeSession.planned_duration
    },

    overtimeMinutes: (state) => {
      if (!state.activeSession) return 0
      const elapsed = state.elapsedMinutes
      return Math.max(0, elapsed - state.activeSession.planned_duration)
    },
  },

  actions: {
    async fetchActiveSession() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/api/sessions/active')
        this.activeSession = response.data

        // Start polling if there's an active session
        if (this.activeSession && !this.pollInterval) {
          this.startPolling()
        } else if (!this.activeSession && this.pollInterval) {
          this.stopPolling()
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchRecentSessions(limit = 20) {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/api/sessions/recent', {
          params: { limit },
        })
        this.recentSessions = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async startSession(sessionData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/api/sessions/', sessionData)
        this.activeSession = response.data
        this.startPolling()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async stopSession(sessionId, reviewData = null) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post(`/api/sessions/${sessionId}/stop`, reviewData)
        this.activeSession = null
        this.stopPolling()
        await this.fetchRecentSessions()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async addNote(sessionId, note) {
      this.error = null
      try {
        const response = await api.post(`/api/sessions/${sessionId}/add-note`, { note })
        this.activeSession = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      }
    },

    async addTime(sessionId, minutes = 15) {
      this.error = null
      try {
        const response = await api.post(`/api/sessions/${sessionId}/add-time`, { minutes })
        this.activeSession = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      }
    },

    async toggleNotifications(sessionId) {
      this.error = null
      try {
        const response = await api.post(`/api/sessions/${sessionId}/toggle-notifications`)
        this.activeSession = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      }
    },

    startPolling() {
      if (this.pollInterval) return

      // Poll every 30 seconds to update elapsed time and check for changes
      this.pollInterval = setInterval(() => {
        // Force a reactive update by triggering getter recalculation
        if (this.activeSession) {
          this.fetchActiveSession()
        }
      }, 30000)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },

    clearError() {
      this.error = null
    },
  },
})
