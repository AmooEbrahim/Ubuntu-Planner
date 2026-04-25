/**
 * SSE client for the chat agent loop.
 *
 * `axios` doesn't surface streaming bodies cleanly in the browser, so we use
 * `fetch` + the WHATWG ReadableStream parser. The exposed API is async
 * iterator-shaped: callers `await for ... of streamMessage(...)` and act on
 * each event.
 */

const SSE_DELIMITER = '\n\n'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:1717'

/** Parse an "event: foo\ndata: {...}" block into { type, data }. */
function parseEvent(block) {
  let type = 'message'
  const dataLines = []
  for (const line of block.split('\n')) {
    if (line.startsWith(':')) continue
    if (line.startsWith('event:')) type = line.slice(6).trim()
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trimStart())
  }
  if (!dataLines.length) return null
  const raw = dataLines.join('\n')
  let data
  try {
    data = JSON.parse(raw)
  } catch {
    data = raw
  }
  return { type, data }
}

async function* readSSE(response) {
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      let idx
      while ((idx = buffer.indexOf(SSE_DELIMITER)) !== -1) {
        const block = buffer.slice(0, idx)
        buffer = buffer.slice(idx + SSE_DELIMITER.length)
        const event = parseEvent(block)
        if (event) yield event
      }
    }
    if (buffer.trim()) {
      const event = parseEvent(buffer)
      if (event) yield event
    }
  } finally {
    try { reader.releaseLock() } catch { /* noop */ }
  }
}

export async function* streamMessage(chatId, content, { signal } = {}) {
  const response = await fetch(`${baseURL}/api/chat/${chatId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify({ content }),
    signal,
  })
  if (!response.ok) {
    const errBody = await response.text().catch(() => '')
    const err = new Error(`Chat send failed (${response.status}): ${errBody || response.statusText}`)
    err.status = response.status
    throw err
  }
  yield* readSSE(response)
}

export async function* streamResume(chatId, { signal } = {}) {
  const response = await fetch(`${baseURL}/api/chat/${chatId}/resume`, {
    method: 'POST',
    headers: { Accept: 'text/event-stream' },
    signal,
  })
  if (!response.ok) {
    const errBody = await response.text().catch(() => '')
    const err = new Error(`Resume failed (${response.status}): ${errBody || response.statusText}`)
    err.status = response.status
    throw err
  }
  yield* readSSE(response)
}

export async function cancelTurn(chatId) {
  await fetch(`${baseURL}/api/chat/${chatId}/cancel`, { method: 'POST' })
}

export async function decideTool(chatId, toolCallId, decision) {
  const response = await fetch(
    `${baseURL}/api/chat/${chatId}/tool-calls/${encodeURIComponent(toolCallId)}/decision`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision }),
    },
  )
  if (!response.ok) {
    const errBody = await response.text().catch(() => '')
    throw new Error(`Decision failed (${response.status}): ${errBody || response.statusText}`)
  }
  return response.json()
}
