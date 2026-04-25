<template>
  <div class="flex gap-3 justify-start">
    <div class="flex-shrink-0 h-8 w-8 rounded-full bg-info/15 text-info text-[11px] font-bold flex items-center justify-center select-none shadow-sm shadow-info/20">⚙</div>
    <div class="max-w-[80%] w-full">
      <Disclosure v-slot="{ open }" :default-open="defaultOpen">
        <div class="glass-card overflow-hidden">
          <DisclosureButton
            class="w-full flex items-center justify-between gap-3 px-3 py-2 text-sm focus:outline-none hover:bg-fg-subtle/5 transition-colors"
          >
            <div class="flex items-center gap-2 min-w-0">
              <span :class="badgeClass" class="badge">{{ statusLabel }}</span>
              <span class="font-mono text-[12px] text-fg-muted truncate">{{ toolName }}</span>
            </div>
            <svg
              class="h-4 w-4 text-fg-subtle flex-shrink-0 transition-transform"
              :class="open ? 'rotate-180' : ''"
              viewBox="0 0 20 20"
              fill="currentColor"
            ><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 11.06l3.71-3.83a.75.75 0 1 1 1.08 1.04l-4.25 4.39a.75.75 0 0 1-1.08 0L5.21 8.27a.75.75 0 0 1 .02-1.06Z" clip-rule="evenodd"/></svg>
          </DisclosureButton>

          <DisclosurePanel class="border-t border-fg-subtle/15 bg-fg-subtle/5 px-3 py-2 space-y-2">
            <div>
              <div class="text-[10px] uppercase tracking-wide text-subtle mb-1">Arguments</div>
              <pre class="text-[12px] text-fg bg-fg-subtle/5 border border-fg-subtle/15 rounded-md p-2 overflow-x-auto">{{ formattedArgs }}</pre>
            </div>
            <div v-if="hasResult">
              <div class="text-[10px] uppercase tracking-wide text-subtle mb-1">Result</div>
              <pre class="text-[12px] text-fg bg-fg-subtle/5 border border-fg-subtle/15 rounded-md p-2 overflow-x-auto max-h-48">{{ formattedResult }}</pre>
            </div>
          </DisclosurePanel>
        </div>

        <div v-if="status === 'pending'" class="flex items-center gap-2 mt-2">
          <button
            type="button"
            class="btn btn-primary btn-sm"
            :disabled="busy"
            @click="$emit('approve')"
          >Approve</button>
          <button
            type="button"
            class="btn btn-secondary btn-sm"
            :disabled="busy"
            @click="$emit('deny')"
          >Deny</button>
          <span class="text-[11px] text-subtle">Confirm to let the AI run this tool.</span>
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
  pending: 'badge-warning',
  executing: 'badge-info',
  complete: 'badge-success',
  denied: 'badge-neutral',
  error: 'badge-danger',
  cancelled: 'badge-neutral',
}

const badgeClass = computed(() => STATUS_BADGES[props.status] ?? 'badge-neutral')
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
