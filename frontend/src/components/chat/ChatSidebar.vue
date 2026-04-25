<template>
  <aside class="flex flex-col h-full border-r border-gray-200 bg-white">
    <div class="px-3 py-3 border-b border-gray-200 flex items-center justify-between gap-2">
      <h2 class="text-sm font-semibold text-gray-700">Chats</h2>
      <button
        type="button"
        class="rounded-md bg-blue-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        :disabled="creating"
        @click="onCreate"
      >+ New</button>
    </div>

    <div class="flex-1 overflow-y-auto">
      <ul v-if="chats.length" class="divide-y divide-gray-100">
        <li v-for="chat in chats" :key="chat.id">
          <button
            type="button"
            class="w-full text-left px-3 py-2.5 hover:bg-gray-50 focus:outline-none focus:bg-gray-50"
            :class="chat.id === activeId ? 'bg-blue-50' : ''"
            @click="$emit('select', chat.id)"
          >
            <div class="flex items-center justify-between gap-2">
              <p class="text-sm font-medium text-gray-900 truncate">{{ chat.title }}</p>
              <span class="text-[10px] text-gray-400 whitespace-nowrap">{{ formatRelative(chat.updated_at) }}</span>
            </div>
          </button>
        </li>
      </ul>
      <div v-else-if="!loading" class="px-4 py-8 text-center text-sm text-gray-400">
        No chats yet. Click <span class="font-medium text-gray-600">+ New</span> to start one.
      </div>
      <div v-if="loading" class="px-4 py-3 text-center text-xs text-gray-400">Loading…</div>
    </div>
  </aside>
</template>

<script setup>
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

defineProps({
  chats: { type: Array, required: true },
  activeId: { type: Number, default: null },
  loading: { type: Boolean, default: false },
  creating: { type: Boolean, default: false },
})

const emit = defineEmits(['select', 'create'])

const onCreate = () => emit('create')
const formatRelative = (ts) => (ts ? dayjs(ts).fromNow() : '')
</script>
