<script setup>
import { ref, reactive, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

const general = reactive({
  language: 'en',
  notification_interval_default: 10,
  session_poll_interval: 120
})

const notificationTypes = [
  { key: 'planning_start', label: 'Planning Start', description: 'When scheduled work time arrives', icon: 'calendar' },
  { key: 'session_end', label: 'Session End', description: 'When session time is up', icon: 'stop' },
  { key: 'session_reminder', label: 'Session Reminder', description: 'Repeated reminders after session ends', icon: 'bell' }
]

const notifications = reactive({
  planning_start: { enabled: true, config: { sound_enabled: true, sound_file: 'complete.oga', sound_repeat: 1 } },
  session_end: { enabled: true, config: { sound_enabled: true, sound_file: 'complete.oga', sound_repeat: 1 } },
  session_reminder: { enabled: true, config: { sound_enabled: true, sound_file: 'dialog-warning.oga', sound_repeat: 2 } }
})

const availableSounds = ref([])
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)

onMounted(async () => {
  await loadSettings()
  await loadAvailableSounds()
  loading.value = false
})

async function loadSettings() {
  const settings = await settingsStore.getAll()
  general.language = settings.language || 'en'
  general.notification_interval_default = settings.notification_interval_default || 10
  general.session_poll_interval = settings.session_poll_interval || 120
  for (const type of notificationTypes) {
    const enabledKey = `notification_${type.key}_enabled`
    const configKey = `notification_${type.key}_configuration`
    if (settings[enabledKey] !== undefined) notifications[type.key].enabled = settings[enabledKey]
    if (settings[configKey]) notifications[type.key].config = settings[configKey]
  }
}

async function loadAvailableSounds() {
  try { availableSounds.value = await settingsStore.getAvailableSounds() }
  catch { availableSounds.value = ['complete.oga', 'dialog-warning.oga'] }
}

async function saveSettings() {
  saving.value = true
  saved.value = false
  try {
    const updates = {
      language: general.language,
      notification_interval_default: general.notification_interval_default,
      session_poll_interval: general.session_poll_interval
    }
    for (const type of notificationTypes) {
      updates[`notification_${type.key}_enabled`] = notifications[type.key].enabled
      updates[`notification_${type.key}_configuration`] = notifications[type.key].config
    }
    await settingsStore.updateMultiple(updates)
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch {
    alert('Failed to save settings.')
  } finally {
    saving.value = false
  }
}

function resetToDefaults() {
  if (!confirm('Reset all settings to defaults?')) return
  general.language = 'en'
  general.notification_interval_default = 10
  general.session_poll_interval = 120
  notificationTypes.forEach(type => {
    notifications[type.key].enabled = true
    notifications[type.key].config = { sound_enabled: true, sound_file: 'complete.oga', sound_repeat: 1 }
  })
}

function previewSound(soundFile) {
  const audio = new Audio(`/api/settings/sounds/${soundFile}`)
  audio.play().catch(() => alert('Failed to play sound preview'))
}
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-5">
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <h1 class="page-title">Settings</h1>
        <p class="page-subtitle">Configure your application preferences</p>
      </div>
      <div class="flex gap-2">
        <button @click="resetToDefaults" class="btn btn-secondary">Reset Defaults</button>
        <button @click="saveSettings" :disabled="saving" class="btn btn-primary">
          <svg v-if="saving" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="animate-spin">
            <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="10"></circle>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
            <polyline points="17 21 17 13 7 13 7 21"></polyline>
            <polyline points="7 3 7 8 15 8"></polyline>
          </svg>
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>

    <div v-if="saved" class="glass-card border-l-4 border-success/60 bg-success/5 flex items-center gap-2 px-4 py-3 text-success text-sm font-medium">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
      Settings saved successfully!
    </div>

    <div v-if="loading" class="glass-card flex flex-col items-center justify-center py-16 px-6 text-muted">
      <div class="spinner mb-4"></div>
      <p>Loading settings...</p>
    </div>

    <div v-else class="space-y-5">
      <!-- AI Configuration — link card -->
      <RouterLink
        to="/settings/ai"
        class="glass-card p-5 flex items-center gap-4 group transition-all duration-200 hover:-translate-y-0.5 hover:shadow-glass-lg"
      >
        <div
          class="w-12 h-12 rounded-xl text-white flex items-center justify-center shadow-md flex-shrink-0"
          style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent))); box-shadow: 0 6px 20px rgba(168, 85, 247, 0.35);"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="22" height="22">
            <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"></path>
            <path d="M19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8z"></path>
          </svg>
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <h2 class="section-title">AI Assistant</h2>
            <span
              class="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-md text-white"
              style="background: linear-gradient(135deg, #a855f7, rgb(var(--accent)));"
            >AI</span>
          </div>
          <p class="text-sm text-muted mt-0.5">Configure model, prompts, and tool permissions</p>
        </div>
        <svg class="text-fg-subtle group-hover:text-accent transition-colors flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
          <line x1="5" y1="12" x2="19" y2="12"></line>
          <polyline points="12 5 19 12 12 19"></polyline>
        </svg>
      </RouterLink>

      <div class="grid gap-5 lg:grid-cols-2">
      <!-- General -->
      <section class="glass-card p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-accent/15 text-accent">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </div>
          <h2 class="section-title">General</h2>
        </div>

        <div class="space-y-5">
          <div>
            <label class="label">Language</label>
            <select v-model="general.language" class="input">
              <option value="en">English</option>
              <option value="fa">فارسی (Persian)</option>
            </select>
          </div>

          <div>
            <label class="label">Default Reminder Interval</label>
            <div class="flex items-center gap-2">
              <input v-model.number="general.notification_interval_default" type="number" min="1" max="120" class="input">
              <span class="text-sm text-muted flex-shrink-0">min</span>
            </div>
            <p class="text-xs text-subtle mt-1.5">How often to remind about unstarted planned work</p>
          </div>

          <div>
            <label class="label">Session Poll Interval</label>
            <div class="flex items-center gap-2">
              <input v-model.number="general.session_poll_interval" type="number" min="10" max="600" class="input">
              <span class="text-sm text-muted flex-shrink-0">sec</span>
            </div>
            <p class="text-xs text-subtle mt-1.5">How often to check for session updates</p>
          </div>
        </div>
      </section>

      <!-- Notifications -->
      <section class="glass-card p-6">
        <div class="flex items-center gap-3 mb-5">
          <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-warning/15 text-warning">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
          </div>
          <h2 class="section-title">Notifications</h2>
        </div>

        <div class="space-y-3">
          <div
            v-for="type in notificationTypes"
            :key="type.key"
            class="glass-inset p-4"
          >
            <div class="flex justify-between items-start gap-4">
              <div>
                <h3 class="text-sm font-semibold text-fg">{{ type.label }}</h3>
                <p class="text-xs text-muted mt-0.5">{{ type.description }}</p>
              </div>
              <label class="relative inline-block cursor-pointer flex-shrink-0">
                <input type="checkbox" v-model="notifications[type.key].enabled" class="sr-only peer">
                <span class="block w-10 h-[22px] bg-fg-subtle/40 peer-checked:bg-accent rounded-full transition-colors"></span>
                <span class="absolute top-[3px] left-[3px] w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-[18px]"></span>
              </label>
            </div>

            <div v-if="notifications[type.key].enabled" class="mt-3 pt-3 border-t border-fg-subtle/15">
              <label class="flex items-center gap-2 cursor-pointer mb-3">
                <input type="checkbox" v-model="notifications[type.key].config.sound_enabled" class="w-4 h-4 cursor-pointer" style="accent-color: rgb(var(--accent));">
                <span class="text-sm text-fg">Play sound</span>
              </label>

              <div v-if="notifications[type.key].config.sound_enabled" class="flex flex-col gap-2 ml-6">
                <div class="flex items-center gap-2">
                  <select v-model="notifications[type.key].config.sound_file" class="input text-sm py-1.5 max-w-[200px]">
                    <option v-for="sound in availableSounds" :key="sound" :value="sound">{{ sound }}</option>
                  </select>
                  <button @click="previewSound(notifications[type.key].config.sound_file)" class="icon-btn !w-8 !h-8 !text-accent" title="Preview sound">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
                      <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                  </button>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs text-muted min-w-[80px]">Play count</span>
                  <select v-model.number="notifications[type.key].config.sound_repeat" class="input text-sm py-1.5 max-w-[200px]">
                    <option :value="1">1×</option>
                    <option :value="2">2×</option>
                    <option :value="3">3×</option>
                    <option :value="4">4×</option>
                    <option :value="5">5×</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      </div>
    </div>
  </div>
</template>
