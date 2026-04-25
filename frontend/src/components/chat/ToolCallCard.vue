<template>
  <div class="flex gap-3 justify-start">
    <div class="flex-shrink-0 h-7 w-7 rounded-full bg-purple-100 text-purple-600 text-[11px] font-semibold flex items-center justify-center select-none">⚙</div>
    <div class="max-w-[80%] w-full">
      <Disclosure v-slot="{ open }" :default-open="defaultOpen">
        <div class="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden">
          <DisclosureButton
            class="w-full flex items-center justify-between gap-3 px-3 py-2 text-sm focus:outline-none hover:bg-gray-50"
          >
            <div class="flex items-center gap-2 min-w-0">
              <span :class="badgeClass" class="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide">{{ statusLabel }}</span>
              <span class="font-mono text-[12px] text-gray-700 truncate">{{ toolName }}</span>
            </div>
            <svg
              class="h-4 w-4 text-gray-400 flex-shrink-0 transition-transform"
              :class="open ? 'rotate-180' : ''"
              viewBox="0 0 20 20"
              fill="currentColor"
            ><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 11.06l3.71-3.83a.75.75 0 1 1 1.08 1.04l-4.25 4.39a.75.75 0 0 1-1.08 0L5.21 8.27a.75.75 0 0 1 .02-1.06Z" clip-rule="evenodd"/></svg>
          </DisclosureButton>

          <DisclosurePanel class="border-t border-gray-100 bg-gray-50/50 px-3 py-2 space-y-2">
            <div>
              <div class="text-[10px] uppercase tracking-wide text-gray-500 mb-1">Arguments</div>
              <pre class="text-[12px] text-gray-700 bg-white border border-gray-200 rounded p-2 overflow-x-auto">{{ formattedArgs }}</pre>
            </div>
            <div v-if="hasResult">
              <div class="text-[10px] uppercase tracking-wide text-gray-500 mb-1">Result</div>
              <pre class="text-[12px] text-gray-700 bg-white border border-gray-200 rounded p-2 overflow-x-auto max-h-48">{{ formattedResult }}</pre>
            </div>
          </DisclosurePanel>
        </div>

        <div v-if="status === 'pending'" class="flex items-center gap-2 mt-2">
          <button
            type="button"
            class="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            :disabled="busy"
            @click="$emit('approve')"
          >Approve</button>
          <button
            type="button"
            class="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            :disabled="busy"
            @click="$emit('deny')"
          >Deny</button>
          <span class="text-[11px] text-gray-500">Confirm to let the AI run this tool.</span>
        </div>
      </Disclosure>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'

const props = defineProps({
  toolName: { type: String, required: true },
  args: { type: [Object, String, Array, Number, Boolean, null], default: null },
  result: { type: [Object, String, Array, Number, Boolean, null], default: null },
  status: { type: String, default: 'complete' },
  busy: { type: Boolean, default: false },
  defaultOpen: { type: Boolean, default: false },
})

defineEmits(['approve', 'deny'])

const STATUS_BADGES = {
  pending: 'bg-amber-100 text-amber-800',
  executing: 'bg-blue-100 text-blue-800',
  complete: 'bg-green-100 text-green-800',
  denied: 'bg-gray-200 text-gray-700',
  error: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-200 text-gray-700',
}

const badgeClass = computed(() => STATUS_BADGES[props.status] ?? 'bg-gray-100 text-gray-600')
const statusLabel = computed(() => props.status)

const hasResult = computed(() => props.result != null)
const formattedArgs = computed(() => formatJSON(props.args))
const formattedResult = computed(() => formatJSON(props.result))

function formatJSON(value) {
  if (value == null) return ''
  if (typeof value === 'string') return value
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}
</script>
