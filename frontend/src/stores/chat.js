import { defineStore } from 'pinia'
import api from '@/services/api'
import { streamMessage, streamResume, cancelTurn, decideTool } from '@/services/aiClient'

export const useChatStore = defineStore('chat', {
  state: () => ({
    chats: [],
    detailById: {},
    loadingList: false,
    loadingChatId: null,
    error: null,
  }),

  getters: {
    chatById: (state) => (id) => state.chats.find((c) => c.id === id) ?? null,
    detail: (state) => (id) => state.detailById[id] ?? null,
    messages: (state) => (id) => state.detailById[id]?.messages ?? [],
  },

  actions: {
    async fetchList(includeArchived = false) {
      this.loadingList = true
      this.error = null
      try {
        const res = await api.get('/api/chat/', { params: { include_archived: includeArchived } })
        this.chats = res.data
      } catch (err) {
        this.error = err.response?.data?.detail || err.message
        throw err
      } finally {
        this.loadingList = false
      }
    },

    async fetchDetail(id) {
      this.loadingChatId = id
      this.error = null
      try {
        const res = await api.get(`/api/chat/${id}`)
        const data = res.data
        // Preserve in-memory suggested_replies set by the live stream when the
        // backend response (race with the DB write) doesn't include them.
        const existing = this.detailById[id]
        if (existing && Array.isArray(existing.messages) && Array.isArray(data.messages)) {
          const memById = new Map(existing.messages.map((m) => [m.id, m]))
          data.messages = data.messages.map((m) => {
            const mem = memById.get(m.id)
            if (mem && Array.isArray(mem.suggested_replies) && mem.suggested_replies.length
                && (!m.suggested_replies || (Array.isArray(m.suggested_replies) && m.suggested_replies.length === 0))) {
              return { ...m, suggested_replies: mem.suggested_replies }
            }
            return m
          })
        }
        this.detailById[id] = data
        const idx = this.chats.findIndex((c) => c.id === id)
        if (idx !== -1) {
          const { messages, permissions, system_prompt_override, model_override, ...summary } = data
          this.chats[idx] = summary
        }
        return data
      } catch (err) {
        this.error = err.response?.data?.detail || err.message
        throw err
      } finally {
        this.loadingChatId = null
      }
    },

    async createChat(title) {
      this.error = null
      try {
        const res = await api.post('/api/chat/', { title: title || null })
        this.detailById[res.data.id] = res.data
        const { messages, permissions, system_prompt_override, model_override, ...summary } = res.data
        this.chats.unshift(summary)
        return res.data
      } catch (err) {
        this.error = err.response?.data?.detail || err.message
        throw err
      }
    },

    async updateChat(id, patch) {
      this.error = null
      try {
        const res = await api.patch(`/api/chat/${id}`, patch)
        this.detailById[id] = res.data
        const idx = this.chats.findIndex((c) => c.id === id)
        if (idx !== -1) {
          const { messages, permissions, system_prompt_override, model_override, ...summary } = res.data
          this.chats[idx] = summary
        }
        return res.data
      } catch (err) {
        this.error = err.response?.data?.detail || err.message
        throw err
      }
    },

    async deleteChat(id) {
      this.error = null
      try {
        await api.delete(`/api/chat/${id}`)
        this.chats = this.chats.filter((c) => c.id !== id)
        delete this.detailById[id]
      } catch (err) {
        this.error = err.response?.data?.detail || err.message
        throw err
      }
    },

    appendLocalMessage(chatId, message) {
      const detail = this.detailById[chatId]
      if (!detail) return
      const existingIdx = detail.messages.findIndex((m) => m.id === message.id)
      if (existingIdx === -1) {
        detail.messages.push(message)
      } else {
        detail.messages[existingIdx] = { ...detail.messages[existingIdx], ...message }
      }
    },

    patchLocalMessage(chatId, messageId, patch) {
      const detail = this.detailById[chatId]
      if (!detail) return
      const idx = detail.messages.findIndex((m) => m.id === messageId)
      if (idx !== -1) {
        detail.messages[idx] = { ...detail.messages[idx], ...patch }
      }
    },

    async sendMessage(chatId, content) {
      await this._consumeStream(chatId, () => streamMessage(chatId, content))
    },

    async resumeTurn(chatId) {
      await this._consumeStream(chatId, () => streamResume(chatId))
    },

    async cancelTurn(chatId) {
      await cancelTurn(chatId)
    },

    async decideTool(chatId, toolCallId, decision) {
      const result = await decideTool(chatId, toolCallId, decision)
      // Refresh the chat to pick up updated tool_use + new tool_result rows.
      await this.fetchDetail(chatId)
      return result
    },

    async _consumeStream(chatId, makeIter) {
      this._ensureDetail(chatId)
      const detail = this.detailById[chatId]
      const streamingMessageIds = new Set()
      try {
        const iter = makeIter()
        for await (const evt of iter) {
          this._applyEvent(detail, evt, streamingMessageIds)
        }
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        // Clear any lingering "streaming" flags on assistant messages.
        for (const id of streamingMessageIds) {
          const idx = detail.messages.findIndex((m) => m.id === id)
          if (idx !== -1 && detail.messages[idx].streaming) {
            detail.messages[idx] = { ...detail.messages[idx], streaming: false }
          }
        }
      }
    },

    _ensureDetail(chatId) {
      if (!this.detailById[chatId]) {
        this.detailById[chatId] = { id: chatId, messages: [] }
      }
    },

    _applyEvent(detail, evt, streamingMessageIds) {
      const { type, data } = evt
      if (type === 'message') {
        this._upsertMessage(detail, data)
        return
      }
      if (type === 'assistant_started') {
        this._upsertMessage(detail, {
          id: data.message_id,
          role: 'assistant',
          content: '',
          streaming: true,
          status: 'executing',
          created_at: new Date().toISOString(),
        })
        streamingMessageIds.add(data.message_id)
        return
      }
      if (type === 'text') {
        const idx = detail.messages.findIndex((m) => m.id === data.message_id)
        if (idx !== -1) {
          const prev = detail.messages[idx]
          detail.messages[idx] = {
            ...prev,
            content: (prev.content || '') + data.delta,
            streaming: true,
          }
        }
        return
      }
      if (type === 'assistant_complete') {
        const idx = detail.messages.findIndex((m) => m.id === data.message_id)
        if (idx !== -1) {
          detail.messages[idx] = {
            ...detail.messages[idx],
            content: data.content ?? detail.messages[idx].content,
            streaming: false,
            status: 'complete',
          }
        }
        streamingMessageIds.delete(data.message_id)
        return
      }
      if (type === 'tool_call_start' || type === 'tool_call_args') {
        // Internal stream noise; ignore in UI.
        return
      }
      if (type === 'tool_call') {
        const id = data.id ?? data.tool_use_id
        if (!id) return
        const existing = detail.messages.find((m) => m.id === id)
        const merged = {
          id,
          role: 'tool_use',
          tool_call_id: data.tool_call_id,
          tool_name: data.tool_name ?? existing?.tool_name ?? '',
          tool_args: data.args ?? existing?.tool_args ?? null,
          status: data.status,
          created_at: existing?.created_at ?? new Date().toISOString(),
        }
        this._upsertMessage(detail, merged)
        return
      }
      if (type === 'tool_result') {
        const idx = detail.messages.findIndex((m) => m.id === data.tool_use_id)
        if (idx !== -1) {
          detail.messages[idx] = {
            ...detail.messages[idx],
            tool_result: data.result,
            status: data.status,
          }
        }
        return
      }
      if (type === 'pending_confirmation') {
        const idx = detail.messages.findIndex((m) => m.id === data.tool_use_id)
        if (idx !== -1) {
          detail.messages[idx] = {
            ...detail.messages[idx],
            status: 'pending',
          }
        }
        return
      }
      if (type === 'suggested_replies') {
        const idx = detail.messages.findIndex((m) => m.id === data.message_id)
        if (idx !== -1) {
          detail.messages[idx] = {
            ...detail.messages[idx],
            suggested_replies: data.suggestions,
          }
        }
        return
      }
      if (type === 'done') {
        // No-op; the finally block clears streaming flags.
        return
      }
      if (type === 'error') {
        this.error = data.message
        return
      }
    },

    _upsertMessage(detail, message) {
      const idx = detail.messages.findIndex((m) => m.id === message.id)
      if (idx === -1) {
        detail.messages.push(message)
      } else {
        detail.messages[idx] = { ...detail.messages[idx], ...message }
      }
    },
  },
})
