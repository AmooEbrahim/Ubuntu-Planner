import { defineStore } from 'pinia'
import dayjs from 'dayjs'
import api from '@/services/api'

const SECTION_FIELDS = [
  'intentions',
  'reflection',
  'lessons',
  'completed',
  'gratitude',
  'free_notes',
]

const emptyEntry = (date, isAi) => ({
  id: null,
  date,
  is_ai: isAi,
  intentions: '',
  reflection: '',
  lessons: '',
  completed: '',
  gratitude: '',
  free_notes: '',
  mood: null,
  created_at: null,
  updated_at: null,
})

const normalizeEntry = (entry) => {
  if (!entry) return null
  const out = { ...entry }
  for (const field of SECTION_FIELDS) {
    out[field] = entry[field] ?? ''
  }
  return out
}

export const useDayMemoryStore = defineStore('dayMemory', {
  state: () => ({
    pairsByDate: {},
    loadingByDate: {},
    savingByDate: {},
    error: null,
  }),

  getters: {
    pairFor: (state) => (date) => {
      const key = dayjs(date).format('YYYY-MM-DD')
      return state.pairsByDate[key] ?? null
    },
    isLoading: (state) => (date) => {
      const key = dayjs(date).format('YYYY-MM-DD')
      return Boolean(state.loadingByDate[key])
    },
    isSaving: (state) => (date, track) => {
      const key = `${dayjs(date).format('YYYY-MM-DD')}:${track}`
      return Boolean(state.savingByDate[key])
    },
  },

  actions: {
    async fetchDate(date) {
      const key = dayjs(date).format('YYYY-MM-DD')
      this.loadingByDate[key] = true
      this.error = null
      try {
        const res = await api.get(`/api/day-memory/${key}`)
        this.pairsByDate[key] = {
          date: res.data.date,
          user: normalizeEntry(res.data.user) ?? emptyEntry(key, false),
          ai: normalizeEntry(res.data.ai) ?? emptyEntry(key, true),
        }
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.loadingByDate[key] = false
      }
    },

    async upsert(date, track, partial) {
      const key = dayjs(date).format('YYYY-MM-DD')
      const savingKey = `${key}:${track}`
      this.savingByDate[savingKey] = true
      this.error = null
      try {
        const path = track === 'ai' ? `/api/day-memory/${key}/ai` : `/api/day-memory/${key}`
        const res = await api.put(path, partial)
        if (!this.pairsByDate[key]) {
          this.pairsByDate[key] = {
            date: key,
            user: emptyEntry(key, false),
            ai: emptyEntry(key, true),
          }
        }
        this.pairsByDate[key][track] = normalizeEntry(res.data)
        return res.data
      } catch (error) {
        this.error = error.response?.data?.detail || error.message
        throw error
      } finally {
        this.savingByDate[savingKey] = false
      }
    },

    setLocalField(date, track, field, value) {
      const key = dayjs(date).format('YYYY-MM-DD')
      if (!this.pairsByDate[key]) {
        this.pairsByDate[key] = {
          date: key,
          user: emptyEntry(key, false),
          ai: emptyEntry(key, true),
        }
      }
      this.pairsByDate[key][track][field] = value
    },
  },
})

export { SECTION_FIELDS, emptyEntry }
