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
        <div class="fixed inset-0 bg-black/30" />
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
          <DialogPanel class="w-screen max-w-md bg-white shadow-xl flex flex-col h-full">
            <header class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
              <DialogTitle class="text-base font-semibold text-gray-900">Permissions for this chat</DialogTitle>
              <button
                type="button"
                class="text-gray-400 hover:text-gray-700"
                @click="$emit('close')"
              >✕</button>
            </header>

            <div class="px-5 py-3 border-b border-gray-100 text-xs text-gray-500">
              Per-chat overrides. Empty selection = use the global default from
              <RouterLink to="/settings/ai" class="text-blue-600 hover:underline">AI settings</RouterLink>.
            </div>

            <ul class="flex-1 overflow-y-auto divide-y divide-gray-100">
              <li
                v-for="t in tools"
                :key="t.name"
                class="px-5 py-3 flex items-start justify-between gap-3"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900 font-mono">{{ t.name }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">{{ t.description }}</p>
                </div>
                <select
                  :value="overrides[t.name] ?? ''"
                  class="text-xs rounded border border-gray-300 px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  @change="onChange(t.name, $event.target.value)"
                >
                  <option value="">default</option>
                  <option value="allow">allow</option>
                  <option value="confirm">confirm</option>
                  <option value="deny">deny</option>
                </select>
              </li>
            </ul>

            <footer class="px-5 py-3 border-t border-gray-200 flex items-center justify-between gap-3">
              <button
                type="button"
                class="text-xs text-gray-500 hover:text-gray-800"
                @click="$emit('clear')"
              >Reset all to defaults</button>
              <button
                type="button"
                class="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
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
