<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    <header>
      <h1 class="text-2xl font-semibold text-gray-900">AI Settings</h1>
      <p class="text-sm text-gray-500 mt-1">
        Configure the model, API endpoint, and global tool permissions. These apply to every chat
        unless a chat overrides them.
      </p>
    </header>

    <div v-if="store.loading" class="text-sm text-gray-500">Loading…</div>
    <div v-if="store.error" class="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">
      {{ store.error }}
    </div>

    <form
      v-if="form"
      class="space-y-6"
      @submit.prevent="onSave"
    >
      <section class="rounded-xl border border-gray-200 bg-white shadow-sm divide-y divide-gray-100">
        <div class="px-5 py-4 flex items-start justify-between gap-4">
          <div>
            <h2 class="text-base font-semibold text-gray-900">Enabled</h2>
            <p class="text-xs text-gray-500 mt-0.5">When off, chat send returns an error.</p>
          </div>
          <Switch
            v-model="form.enabled"
            :class="form.enabled ? 'bg-blue-600' : 'bg-gray-200'"
            class="relative inline-flex h-6 w-11 items-center rounded-full transition"
          >
            <span :class="form.enabled ? 'translate-x-6' : 'translate-x-1'" class="inline-block h-4 w-4 transform rounded-full bg-white transition" />
          </Switch>
        </div>
      </section>

      <section class="rounded-xl border border-gray-200 bg-white shadow-sm">
        <header class="px-5 py-3 border-b border-gray-100">
          <h2 class="text-base font-semibold text-gray-900">Provider</h2>
        </header>
        <div class="px-5 py-4 space-y-4">
          <Field label="Model">
            <input v-model="form.model" type="text" class="form-input" placeholder="openai/gpt-oss-120b:free" />
          </Field>
          <Field label="Base URL">
            <input v-model="form.base_url" type="url" class="form-input" placeholder="https://openrouter.ai/api/v1" />
          </Field>
          <Field label="API key">
            <input
              v-model="form.api_key"
              :type="showKey ? 'text' : 'password'"
              autocomplete="off"
              class="form-input"
            />
            <button
              type="button"
              class="text-xs text-gray-500 hover:text-gray-800 mt-1"
              @click="showKey = !showKey"
            >{{ showKey ? 'Hide' : 'Show' }} key</button>
          </Field>
          <Field label="Request timeout (seconds)">
            <input v-model.number="form.request_timeout" type="number" min="10" max="600" class="form-input w-32" />
          </Field>
          <Field label="Max tool iterations per turn">
            <input v-model.number="form.max_tool_iterations" type="number" min="1" max="50" class="form-input w-32" />
          </Field>
          <Field label="System prompt">
            <textarea v-model="form.system_prompt" rows="5" class="form-input"></textarea>
          </Field>
        </div>
      </section>

      <section class="rounded-xl border border-gray-200 bg-white shadow-sm">
        <header class="px-5 py-3 border-b border-gray-100">
          <h2 class="text-base font-semibold text-gray-900">About you</h2>
          <p class="text-xs text-gray-500 mt-0.5">
            Anything you want the AI to know about you — your role, preferences, daily rhythms, hard rules.
            This is added to the system prompt of every chat. Keep it concise (a paragraph or two is plenty).
          </p>
        </header>
        <div class="px-5 py-4">
          <textarea
            v-model="form.user_prompt"
            rows="6"
            class="form-input"
            placeholder="I'm a graduate student. I prefer deep-work blocks of 50 min. I usually study from 09:00 to 13:00, then again 17:00–20:00. Reply in English unless I switch to Persian. Don't suggest tasks before 09:00 or after 22:00."
          ></textarea>
        </div>
      </section>

      <section class="rounded-xl border border-gray-200 bg-white shadow-sm">
        <header class="px-5 py-3 border-b border-gray-100">
          <h2 class="text-base font-semibold text-gray-900">Tool permissions</h2>
          <p class="text-xs text-gray-500 mt-0.5">
            <span class="font-medium">allow</span> = run silently.
            <span class="font-medium">confirm</span> = pause for your approval.
            <span class="font-medium">deny</span> = hide from the AI entirely.
          </p>
        </header>
        <ul class="divide-y divide-gray-100">
          <li
            v-for="t in store.tools"
            :key="t.name"
            class="px-5 py-3 flex items-start justify-between gap-4"
          >
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-gray-900 font-mono">{{ t.name }}</p>
              <p class="text-xs text-gray-500 mt-0.5">{{ t.description }}</p>
              <span
                class="inline-flex mt-1 text-[10px] uppercase tracking-wide rounded-full px-2 py-0.5"
                :class="tierClass(t.permission_tier)"
              >{{ t.permission_tier }} (default {{ t.default_level }})</span>
            </div>
            <select
              :value="form.permissions[t.name] ?? ''"
              class="form-input w-32"
              @change="onPermChange(t.name, $event.target.value)"
            >
              <option value="">— default —</option>
              <option value="allow">allow</option>
              <option value="confirm">confirm</option>
              <option value="deny">deny</option>
            </select>
          </li>
        </ul>
      </section>

      <div class="flex items-center gap-3 sticky bottom-0 bg-gray-50/90 backdrop-blur py-3 border-t border-gray-200">
        <button
          type="submit"
          :disabled="store.saving"
          class="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >{{ store.saving ? 'Saving…' : 'Save' }}</button>
        <button
          type="button"
          class="text-sm text-gray-600 hover:text-gray-900"
          @click="reset"
        >Discard changes</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed, h, onMounted, reactive, ref } from 'vue'
import { Switch } from '@headlessui/vue'
import { toast } from 'vue-sonner'
import { useAISettingsStore } from '@/stores/aiSettings'

const store = useAISettingsStore()
const form = ref(null)
const showKey = ref(false)

const Field = (props, { slots }) =>
  h('label', { class: 'block' }, [
    h('span', { class: 'block text-sm font-medium text-gray-700 mb-1' }, props.label),
    slots.default ? slots.default() : null,
  ])
Field.props = ['label']

const tierClass = (tier) => {
  if (tier === 'destructive') return 'bg-red-100 text-red-800'
  if (tier === 'write') return 'bg-amber-100 text-amber-800'
  return 'bg-green-100 text-green-800'
}

const onPermChange = (name, value) => {
  if (!value) {
    delete form.value.permissions[name]
  } else {
    form.value.permissions = { ...form.value.permissions, [name]: value }
  }
}

const reset = () => {
  if (!store.config) return
  form.value = JSON.parse(JSON.stringify(store.config))
  form.value.permissions = { ...(store.config.permissions || {}) }
}

const onSave = async () => {
  try {
    await store.update({
      enabled: form.value.enabled,
      model: form.value.model,
      base_url: form.value.base_url,
      api_key: form.value.api_key,
      system_prompt: form.value.system_prompt,
      user_prompt: form.value.user_prompt,
      permissions: form.value.permissions,
      request_timeout: form.value.request_timeout,
      max_tool_iterations: form.value.max_tool_iterations,
    })
    reset()
    toast.success('AI settings saved.')
  } catch (err) {
    toast.error(err.message || 'Failed to save AI settings.')
  }
}

onMounted(async () => {
  await store.fetch()
  reset()
})
</script>

<style scoped>
.form-input {
  display: block;
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid rgb(209 213 219);
  background-color: white;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: rgb(17 24 39);
  outline: none;
}
.form-input:focus {
  border-color: rgb(59 130 246);
  box-shadow: 0 0 0 1px rgb(59 130 246);
}
</style>
