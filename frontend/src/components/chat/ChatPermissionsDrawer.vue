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
          <DialogPanel class="w-screen max-w-md glass-panel !rounded-none flex flex-col h-full">
            <header class="px-5 py-4 border-b border-fg-subtle/15 flex items-center justify-between">
              <DialogTitle class="text-base font-bold text-fg">Permissions for this chat</DialogTitle>
              <button
                type="button"
                class="icon-btn"
                @click="$emit('close')"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </header>

            <div class="px-5 py-3 border-b border-fg-subtle/15 text-xs text-muted">
              Per-chat overrides. Empty selection = use the global default from
              <RouterLink to="/settings/ai" class="text-accent hover:underline">AI settings</RouterLink>.
            </div>

            <ul class="flex-1 overflow-y-auto divide-y divide-fg-subtle/10">
              <li
                v-for="t in tools"
                :key="t.name"
                class="px-5 py-3 flex items-start justify-between gap-3"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-semibold text-fg font-mono">{{ t.name }}</p>
                  <p class="text-xs text-muted mt-0.5">{{ t.description }}</p>
                </div>
                <select
                  :value="overrides[t.name] ?? ''"
                  class="input text-xs py-1 px-2 w-auto"
                  @change="onChange(t.name, $event.target.value)"
                >
                  <option value="">default</option>
                  <option value="allow">allow</option>
                  <option value="confirm">confirm</option>
                  <option value="deny">deny</option>
                </select>
              </li>
            </ul>

            <footer class="px-5 py-3 border-t border-fg-subtle/15 flex items-center justify-between gap-3">
              <button
                type="button"
                class="text-xs text-muted hover:text-fg transition-colors"
                @click="$emit('clear')"
              >Reset all to defaults</button>
              <button
                type="button"
                class="btn btn-primary btn-sm"
                @click="$emit('close')"
              >Done</button>
            </footer>
          </DialogPanel>
        </TransitionChild>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { RouterLink } from 'vue-router'

defineProps({
  open: { type: Boolean, default: false },
  tools: { type: Array, required: true },
  overrides: { type: Object, required: true },
})

const emit = defineEmits(['close', 'change', 'clear'])

const onChange = (name, value) => {
  emit('change', { name, level: value || null })
}
</script>
