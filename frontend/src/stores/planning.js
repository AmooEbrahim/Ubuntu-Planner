import { defineStore } from 'pinia'
import api from '@/services/api'
import dayjs from 'dayjs'

export const usePlanningStore = defineStore('planning', {
  state: () => ({
    planning: [],
    currentDate: dayjs().format('YYYY-MM-DD'),
    loading: false,
    error: null,
  }),

  getters: {
    todayPlanning: (state) => {
      const today = dayjs().format('YYYY-MM-DD')
      return state.planning.filter((p) =>
        dayjs(p.scheduled_start).format('YYYY-MM-DD') === today
      )
    },

    planningByDate: (state) => (date) => {
      const dateStr = dayjs(date).format('YYYY-MM-DD')
      return state.planning.filter((p) =>
        dayjs(p.scheduled_start).format('YYYY-MM-DD') === dateStr
      ).sort((a, b) => new Date(a.scheduled_start) - new Date(b.scheduled_start))
    },

    planningById: (state) => (id) => {
      return state.planning.find((p) => p.id === id)
    },
  },

  actions: {
    async fetchPlanningForDate(date) {
      this.loading = true
      this.error = null
      try {
        const dateStr = dayjs(date).format('YYYY-MM-DD')
        const response = await api.get('/api/planning/', {
          params: { date: dateStr },
        })
        this.planning = response.data
        this.currentDate = dateStr
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchAllPlanning() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/api/planning/')
        this.planning = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTodayPlanning() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/api/planning/today')
        this.planning = response.data
        this.currentDate = dayjs().format('YYYY-MM-DD')
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async createPlanning(planningData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/api/planning/', planningData)
        this.planning.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async updatePlanning(planningId, planningData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.put(`/api/planning/${planningId}`, planningData)
        const index = this.planning.findIndex((p) => p.id === planningId)
        if (index !== -1) {
          this.planning[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async deletePlanning(planningId) {
      this.loading = true
      this.error = null
      try {
        await api.delete(`/api/planning/${planningId}`)
        this.planning = this.planning.filter((p) => p.id !== planningId)
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    setCurrentDate(date) {
      this.currentDate = dayjs(date).format('YYYY-MM-DD')
    },

    clearError() {
      this.error = null
    },
  },
})
