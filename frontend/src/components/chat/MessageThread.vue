<template>
  <div ref="scrollEl" class="flex-1 min-h-0 overflow-y-auto px-4 sm:px-6 py-5 space-y-4 bg-gray-50">
    <div v-if="!groups.length" class="h-full flex items-center justify-center">
      <div class="text-center max-w-md">
        <div class="mx-auto mb-3 h-12 w-12 rounded-2xl bg-blue-100 text-blue-600 flex items-center justify-center text-xl">💬</div>
        <h3 class="text-lg font-semibold text-gray-900">Say hi to your planner</h3>
        <p class="text-sm text-gray-500 mt-1">Ask about today's plan, start a session, or write a journal entry — the AI can help.</p>
      </div>
    </div>

    <template v-for="group in groups" :key="group.key">
      <MessageBubble
        v-if="group.kind === 'message'"
        :role="group.message.role"
        :content="group.message.content"
        :streaming="group.message.streaming"
        :meta="group.message.meta"
      />
      <template v-else>
        <ToolCallCard
          v-if="!hideTools || group.toolUse.status === 'pending'"
          :tool-name="group.toolUse.tool_name || 'tool'"
          :args="group.toolUse.tool_args"
          :result="group.result?.tool_result"
          :status="group.toolUse.status"
          :busy="group.busy"
          :default-open="group.toolUse.status === 'pending' || group.toolUse.status === 'error'"
          @approve="$emit('approve-tool', group.toolUse)"
          @deny="$emit('deny-tool', group.toolUse)"
        />
      </template>
    </template>

    <SuggestedReplies
      v-if="latestSuggestions.length"
      :suggestions="latestSuggestions"
      :disabled="disablePicks"
      @pick="$emit('pick-reply', $event)"
    />
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import MessageBubble from './MessageBubble.vue'
import ToolCallCard from './ToolCallCard.vue'
import SuggestedReplies from './SuggestedReplies.vue'

const props = defineProps({
  messages: { type: Array, required: true },
  hideTools: { type: Boolean, default: false },
  disablePicks: { type: Boolean, default: false },
})

defineEmits(['approve-tool', 'deny-tool', 'pick-reply'])

const latestSuggestions = computed(() => {
  // Show suggestions only on the most recent assistant message that's
  // already complete (not streaming) and has any pending tool calls cleared.
  for (let i = props.messages.length - 1; i >= 0; i--) {
    const m = props.messages[i]
    if (m.role === 'tool_use' && m.status === 'pending') return []
    if (m.role !== 'assistant') continue
    if (m.streaming) return []
    if (Array.isArray(m.suggested_replies) && m.suggested_replies.length) {
      return m.suggested_replies
    }
    return []
  }
  return []
})

const scrollEl = ref(null)

const groups = computed(() => {
  const result = []
  const usedResults = new Set()

  for (const m of props.messages) {
    if (m.role === 'tool_use') {
      const matchingResult = props.messages.find(
        (r) => r.role === 'tool_result' && r.tool_call_id === m.tool_call_id,
      )
      if (matchingResult) usedResults.add(matchingResult.id)
      result.push({
        kind: 'tool',
        key: `tool-${m.id}`,
        toolUse: m,
        result: matchingResult ?? null,
        busy: false,
      })
      continue
    }
    if (m.role === 'tool_result') {
      if (usedResults.has(m.id)) continue
      // Orphan result (shouldn't normally happen) — render as system note
      result.push({
        kind: 'message',
        key: `msg-${m.id}`,
        message: {
          id: m.id,
          role: 'assistant',
          content: typeof m.tool_result === 'string' ? m.tool_result : JSON.stringify(m.tool_result),
          streaming: false,
          meta: 'tool result',
        },
      })
      continue
    }
    if (m.role === 'system') continue
    result.push({
      kind: 'message',
      key: `msg-${m.id}`,
      message: {
        id: m.id,
        role: m.role,
        content: m.content ?? '',
        streaming: m.streaming ?? false,
        meta: m.model && m.role === 'assistant' ? m.model : '',
      },
    })
  }

  return result
})

const scrollToBottom = () => {
  if (!scrollEl.value) return
  scrollEl.value.scrollTop = scrollEl.value.scrollHeight
}

watch(
  () => props.messages.length,
  () => nextTick(scrollToBottom),
)

watch(
  () => props.messages.map((m) => m.content).join('|'),
  () => nextTick(scrollToBottom),
)
</script>
