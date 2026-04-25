<template>
  <div ref="scrollEl" class="flex-1 min-h-0 overflow-y-auto pt-6 pb-2 px-4">
    <div class="max-w-3xl mx-auto space-y-5">
      <div v-if="!groups.length" class="flex items-center justify-center py-16">
        <div class="text-center max-w-md">
          <div
            class="mx-auto mb-4 h-16 w-16 rounded-2xl text-white flex items-center justify-center shadow-md"
            style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent))); box-shadow: 0 8px 24px rgba(168, 85, 247, 0.35);"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="28" height="28">
              <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"></path>
              <path d="M19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8z"></path>
            </svg>
          </div>
          <h3 class="text-lg font-bold text-fg">Say hi to your planner</h3>
          <p class="text-sm text-muted mt-1">Ask about today's plan, start a session, or write a journal entry — the AI can help.</p>
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
