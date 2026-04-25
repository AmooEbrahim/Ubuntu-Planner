<template>
  <div class="h-full p-3 flex flex-col overflow-hidden">
    <div class="glass-card flex flex-col flex-1 min-h-0 overflow-hidden">
      <!-- Header -->
      <header class="flex-shrink-0 border-b border-fg-subtle/15 px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3 min-w-0 flex-1">
          <div
            class="w-10 h-10 rounded-xl text-white flex items-center justify-center shadow-md flex-shrink-0"
            style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent))); box-shadow: 0 4px 16px rgba(168, 85, 247, 0.35);"
            aria-hidden="true"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
              <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"></path>
              <path d="M19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8z"></path>
            </svg>
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-1.5 min-w-0">
              <h1 v-if="activeChat" class="text-base font-bold text-fg truncate">{{ activeChat.title }}</h1>
              <h1 v-else class="text-base font-bold text-fg-subtle">No conversation</h1>
              <button
                v-if="activeChat"
                type="button"
                class="flex-shrink-0 w-6 h-6 rounded-md text-fg-subtle hover:text-accent hover:bg-accent/10 flex items-center justify-center transition-colors"
                @click="onRename"
                title="Rename"
                aria-label="Rename chat"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="12" height="12">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
            </div>
            <p v-if="activeChat" class="text-[11px] text-subtle truncate">AI Assistant</p>
            <p v-else class="text-[11px] text-subtle">Start a conversation to begin</p>
          </div>
        </div>

        <div class="flex items-center gap-1.5 flex-shrink-0">
          <button
            v-if="activeChat"
            type="button"
            class="hidden sm:inline-flex btn btn-secondary btn-sm !text-fg-muted hover:!text-fg"
            :title="hideTools ? 'Tool calls hidden — click to show' : 'Hide tool calls'"
            @click="hideTools = !hideTools"
          >{{ hideTools ? 'Show tools' : 'Hide tools' }}</button>

          <button
            v-if="activeChat"
            type="button"
            class="icon-btn"
            @click="permissionsOpen = true"
            title="Permissions"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </button>

          <button
            type="button"
            class="btn btn-secondary btn-sm"
            @click="historyOpen = true"
            title="Chat history"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
            <span class="hidden sm:inline">History</span>
          </button>

          <button
            type="button"
            class="btn btn-primary btn-sm"
            :disabled="creating"
            @click="onCreate"
            title="New conversation"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            <span class="hidden sm:inline">New</span>
          </button>
        </div>
      </header>

      <!-- Messages or empty state -->
      <MessageThread
        v-if="activeChat"
        :messages="messages"
        :hide-tools="hideTools"
        :disable-picks="streaming"
        @approve-tool="onApproveTool"
        @deny-tool="onDenyTool"
        @pick-reply="onPickReply"
      />
      <div v-else class="flex-1 flex items-center justify-center px-6">
        <div class="text-center max-w-md">
          <div
            class="mx-auto mb-5 w-20 h-20 rounded-3xl text-white flex items-center justify-center shadow-lg"
            style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent))); box-shadow: 0 12px 40px rgba(168, 85, 247, 0.4);"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="36" height="36">
              <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"></path>
              <path d="M19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8z"></path>
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-fg mb-2">Hi! How can I help?</h2>
          <p class="text-base text-muted mb-6">Ask about your plans, sessions, or anything else — I can also use tools to make changes for you.</p>
          <button
            type="button"
            :disabled="creating"
            class="btn btn-primary btn-lg"
            @click="onCreate"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            {{ creating ? 'Creating…' : 'Start new conversation' }}
          </button>
          <button
            v-if="store.chats.length"
            type="button"
            class="btn btn-ghost btn-sm mt-3"
            @click="historyOpen = true"
          >
            Or open a previous one ({{ store.chats.length }})
          </button>
        </div>
      </div>

      <ChatInput
        v-if="activeChat"
        ref="inputRef"
        :disabled="!activeChat || streaming"
        :streaming="streaming"
        :placeholder="streaming ? 'Streaming…' : 'Ask anything…'"
        @send="onSend"
        @cancel="onCancel"
      />
    </div>

    <ChatHistoryDrawer
      :open="historyOpen"
      :chats="store.chats"
      :active-id="activeChatId"
      :loading="store.loadingList"
      :creating="creating"
      @close="historyOpen = false"
      @select="onSelectFromDrawer"
      @create="onCreateFromDrawer"
      @delete="onDeleteFromDrawer"
    />

    <ChatPermissionsDrawer
      :open="permissionsOpen"
      :tools="aiSettings.tools"
      :overrides="chatPermissions"
      @close="permissionsOpen = false"
      @change="onPermissionChange"
      @clear="onPermissionsClear"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import MessageThread from '@/components/chat/MessageThread.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import ChatHistoryDrawer from '@/components/chat/ChatHistoryDrawer.vue'
import ChatPermissionsDrawer from '@/components/chat/ChatPermissionsDrawer.vue'
import { useChatStore } from '@/stores/chat'
import { useAISettingsStore } from '@/stores/aiSettings'

const route = useRoute()
const router = useRouter()
const store = useChatStore()
const aiSettings = useAISettingsStore()

const activeChatId = ref(route.params.id ? Number(route.params.id) : null)
const creating = ref(false)
const streaming = ref(false)
const permissionsOpen = ref(false)
const historyOpen = ref(false)
const inputRef = ref(null)
const HIDE_TOOLS_KEY = 'ubuntu-planner.chat.hide-tools'
const hideTools = ref(typeof localStorage !== 'undefined' && localStorage.getItem(HIDE_TOOLS_KEY) === '1')

watch(hideTools, (v) => {
  try { localStorage.setItem(HIDE_TOOLS_KEY, v ? '1' : '0') } catch { /* ignore */ }
})

const activeDetail = computed(() => (activeChatId.value ? store.detail(activeChatId.value) : null))
const chatPermissions = computed(() => activeDetail.value?.permissions ?? {})

const onPermissionChange = async ({ name, level }) => {
  if (!activeChatId.value) return
  const next = { ...(activeDetail.value?.permissions ?? {}) }
  if (level == null) delete next[name]
  else next[name] = level
  await store.updateChat(activeChatId.value, { permissions: next })
}

const onPermissionsClear = async () => {
  if (!activeChatId.value) return
  await store.updateChat(activeChatId.value, { permissions: {} })
}

const activeChat = computed(() => (activeChatId.value ? store.chatById(activeChatId.value) : null))
const messages = computed(() =>
  activeChatId.value ? store.messages(activeChatId.value) : [],
)

const onSelect = (id) => {
  activeChatId.value = id
  router.replace({ name: 'chat-detail', params: { id } }).catch(() => {})
  store.fetchDetail(id)
}

const onSelectFromDrawer = (id) => {
  historyOpen.value = false
  onSelect(id)
}

const onCreate = async () => {
  creating.value = true
  try {
    const chat = await store.createChat()
    onSelect(chat.id)
  } finally {
    creating.value = false
  }
}

const onCreateFromDrawer = async () => {
  await onCreate()
  historyOpen.value = false
}

const onDeleteFromDrawer = async (id) => {
  await store.deleteChat(id)
  if (id === activeChatId.value) {
    activeChatId.value = null
    router.replace({ name: 'chat' }).catch(() => {})
    if (store.chats.length) {
      onSelect(store.chats[0].id)
      historyOpen.value = false
    }
  }
}

const onRename = async () => {
  if (!activeChat.value) return
  const next = window.prompt('New chat title', activeChat.value.title)
  if (!next || next === activeChat.value.title) return
  await store.updateChat(activeChat.value.id, { title: next })
}

const onSend = async (content) => {
  if (!activeChat.value) return
  streaming.value = true
  try {
    await store.sendMessage(activeChat.value.id, content)
  } catch (err) {
    toast.error(err.message || 'Failed to send message.')
  } finally {
    streaming.value = false
    if (activeChat.value) await store.fetchDetail(activeChat.value.id)
  }
}

const onPickReply = (text) => onSend(text)

const onCancel = async () => {
  if (!activeChat.value) return
  await store.cancelTurn(activeChat.value.id)
}

const onApproveTool = async (toolUse) => {
  if (!activeChat.value) return
  streaming.value = true
  try {
    await store.decideTool(activeChat.value.id, toolUse.tool_call_id, 'approve')
    toast.success(`Ran ${toolUse.tool_name}`)
    await store.resumeTurn(activeChat.value.id)
  } catch (err) {
    toast.error(err.message || 'Failed to approve tool call.')
  } finally {
    streaming.value = false
    if (activeChat.value) await store.fetchDetail(activeChat.value.id)
  }
}

const onDenyTool = async (toolUse) => {
  if (!activeChat.value) return
  streaming.value = true
  try {
    await store.decideTool(activeChat.value.id, toolUse.tool_call_id, 'deny')
    toast.message(`Denied ${toolUse.tool_name}`)
    await store.resumeTurn(activeChat.value.id)
  } catch (err) {
    toast.error(err.message || 'Failed to deny tool call.')
  } finally {
    streaming.value = false
    if (activeChat.value) await store.fetchDetail(activeChat.value.id)
  }
}

// Auto-focus the chat input when the user starts typing anywhere on the page
function handleGlobalKeydown(e) {
  if (!activeChat.value) return
  if (historyOpen.value || permissionsOpen.value) return
  if (e.metaKey || e.ctrlKey || e.altKey) return
  // Skip non-printable / navigation keys
  if (e.key.length !== 1) return
  // Already typing in some input?
  const el = document.activeElement
  if (!el) return
  const tag = el.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || el.isContentEditable) return
  inputRef.value?.focus()
  // Don't preventDefault — the browser will deliver this character to the now-focused textarea
}

onMounted(async () => {
  document.addEventListener('keydown', handleGlobalKeydown)
  await Promise.all([store.fetchList(), aiSettings.fetch()])
  // Always auto-load the latest chat if user landed on /chat without an id
  if (activeChatId.value && store.chatById(activeChatId.value)) {
    await store.fetchDetail(activeChatId.value)
  } else if (!activeChatId.value && store.chats.length) {
    onSelect(store.chats[0].id)
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeydown)
})

watch(
  () => route.params.id,
  (next) => {
    const id = next ? Number(next) : null
    if (id !== activeChatId.value) {
      activeChatId.value = id
      if (id) store.fetchDetail(id)
    }
  },
)
</script>
