<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-50" @close="$emit('close')">
      <TransitionChild
        as="template"
        enter="ease-out duration-200"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-150"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm dark:bg-black/60" />
      </TransitionChild>

      <div class="fixed inset-y-0 right-0 flex max-w-full">
        <TransitionChild
          as="template"
          enter="transform transition ease-in-out duration-300"
          enter-from="translate-x-full"
          enter-to="translate-x-0"
          leave="transform transition ease-in-out duration-200"
          leave-from="translate-x-0"
          leave-to="translate-x-full"
        >
          <DialogPanel class="w-screen max-w-sm glass-panel !rounded-none flex flex-col h-full">
            <header class="px-5 py-4 border-b border-fg-subtle/15 flex items-center justify-between gap-2">
              <DialogTitle class="text-base font-bold text-fg flex items-center gap-2">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18" class="text-accent">
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                </svg>
                Chat history
              </DialogTitle>
              <button
                type="button"
                class="icon-btn"
                @click="$emit('close')"
                aria-label="Close"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </header>

            <div class="px-3 py-3 border-b border-fg-subtle/15">
              <button
                type="button"
                class="btn btn-primary w-full"
                :disabled="creating"
                @click="$emit('create')"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                {{ creating ? 'Creating…' : 'New conversation' }}
              </button>
            </div>

            <div class="flex-1 overflow-y-auto px-2 py-2">
              <ul v-if="chats.length" class="space-y-1">
                <li
                  v-for="chat in chats"
                  :key="chat.id"
                  class="group relative"
                >
                  <div
                    class="w-full px-3 py-2.5 rounded-xl transition-colors flex items-center gap-3 cursor-pointer"
                    :class="chat.id === activeId
                      ? 'bg-accent/15'
                      : 'hover:bg-fg-subtle/10'"
                    role="button"
                    tabindex="0"
                    @click="$emit('select', chat.id)"
                    @keydown.enter="$emit('select', chat.id)"
                    @keydown.space.prevent="$emit('select', chat.id)"
                  >
                    <div
                      class="w-9 h-9 rounded-xl text-white flex items-center justify-center shadow-sm flex-shrink-0"
                      style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent)));"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                        <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"></path>
                      </svg>
                    </div>
                    <div class="min-w-0 flex-1">
                      <p
                        class="text-sm font-semibold truncate"
                        :class="chat.id === activeId ? 'text-accent' : 'text-fg'"
                      >{{ chat.title }}</p>
                      <p class="text-[11px] text-subtle mt-0.5">{{ formatRelative(chat.updated_at) }}</p>
                    </div>
                    <button
                      type="button"
                      class="opacity-0 group-hover:opacity-100 focus:opacity-100 w-7 h-7 rounded-lg flex items-center justify-center text-fg-subtle hover:bg-danger/15 hover:text-danger transition-all flex-shrink-0"
                      @click.stop="onDelete(chat)"
                      :title="`Delete ${chat.title}`"
                      aria-label="Delete chat"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                </li>
              </ul>
              <div v-else-if="!loading" class="px-4 py-12 text-center">
                <div
                  class="mx-auto mb-3 w-14 h-14 rounded-2xl text-white flex items-center justify-center shadow-md"
                  style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent)));"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="24" height="24">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  </svg>
                </div>
                <p class="text-sm text-fg font-semibold">No conversations yet</p>
                <p class="text-xs text-subtle mt-1">Start your first chat above.</p>
              </div>
              <div v-if="loading" class="px-4 py-3 text-center text-xs text-subtle">Loading…</div>
            </div>
          </DialogPanel>
        </TransitionChild>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

const props = defineProps({
  open: { type: Boolean, default: false },
  chats: { type: Array, required: true },
  activeId: { type: Number, default: null },
  loading: { type: Boolean, default: false },
  creating: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'select', 'create', 'delete'])

const formatRelative = (ts) => (ts ? dayjs(ts).fromNow() : '')

const onDelete = (chat) => {
  if (!window.confirm(`Delete "${chat.title}"?`)) return
  emit('delete', chat.id)
}
</script>
