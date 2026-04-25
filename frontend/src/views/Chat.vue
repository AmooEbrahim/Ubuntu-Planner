<template>
  <div class="h-full grid grid-cols-1 md:grid-cols-[18rem_1fr] bg-gray-50 overflow-hidden">
    <ChatSidebar
      :chats="store.chats"
      :active-id="activeChatId"
      :loading="store.loadingList"
      :creating="creating"
      @select="onSelect"
      @create="onCreate"
    />

    <section class="flex flex-col h-full min-h-0 bg-white">
      <header
        class="flex-shrink-0 border-b border-gray-200 px-4 sm:px-6 py-3 flex items-center justify-between gap-3"
      >
        <div class="min-w-0 flex-1">
          <h1 v-if="activeChat" class="text-base font-semibold text-gray-900 truncate">{{ activeChat.title }}</h1>
          <h1 v-else class="text-base font-semibold text-gray-400">No chat selected</h1>
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="activeChat"
            type="button"
            class="rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-gray-50"
            :class="hideTools
              ? 'border-blue-300 bg-blue-50 text-blue-700'
              : 'border-gray-300 bg-white text-gray-700'"
            :title="hideTools ? 'Tool calls are hidden — click to show' : 'Hide tool calls'"
            @click="hideTools = !hideTools"
          >{{ hideTools ? 'Show tools' : 'Hide tools' }}</button>
          <button
            v-if="activeChat"
            type="button"
            class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
            @click="permissionsOpen = true"
          >Permissions</button>
          <button
            v-if="activeChat"
            type="button"
            class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
            @click="onRename"
          >Rename</button>
          <button
            v-if="activeChat"
            type="button"
            class="rounded-md border border-red-200 bg-white px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50"
            @click="onDelete"
          >Delete</button>
        </div>
      </header>

      <MessageThread
        v-if="activeChat"
        :messages="messages"
        :hide-tools="hideTools"
        :disable-picks="streaming"
        @approve-tool="onApproveTool"
        @deny-tool="onDenyTool"
        @pick-reply="onPickReply"
      />
      <div v-else class="flex-1 flex items-center justify-center bg-gray-50 text-sm text-gray-400 px-6 text-center">
        Pick a chat from the sidebar — or create a new one — to start talking.
      </div>

      <ChatInput
        v-if="activeChat"
        :disabled="!activeChat || streaming"
        :streaming="streaming"
        :placeholder="streaming ? 'Streaming…' : 'Ask anything…'"
        @send="onSend"
        @cancel="onCancel"
      />
    </section>

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
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import ChatSidebar from '@/components/chat/ChatSidebar.vue'
import MessageThread from '@/components/chat/MessageThread.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
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

const onCreate = async () => {
  creating.value = true
  try {
    const chat = await store.createChat()
    onSelect(chat.id)
  } finally {
    creating.value = false
  }
}

const onRename = async () => {
  if (!activeChat.value) return
  const next = window.prompt('New chat title', activeChat.value.title)
  if (!next || next === activeChat.value.title) return
  await store.updateChat(activeChat.value.id, { title: next })
}

const onDelete = async () => {
  if (!activeChat.value) return
  if (!window.confirm(`Delete "${activeChat.value.title}"?`)) return
  const id = activeChat.value.id
  await store.deleteChat(id)
  activeChatId.value = null
  router.replace({ name: 'chat' }).catch(() => {})
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

onMounted(async () => {
  await Promise.all([store.fetchList(), aiSettings.fetch()])
  if (activeChatId.value && store.chatById(activeChatId.value)) {
    await store.fetchDetail(activeChatId.value)
  } else if (!activeChatId.value && store.chats.length) {
    onSelect(store.chats[0].id)
  }
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
