<script setup>
import { ref, reactive, onMounted } from 'vue'
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
  <div class="settings-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Settings</h1>
        <p class="page-subtitle">Configure your application preferences</p>
      </div>
      <div class="header-actions">
        <button @click="resetToDefaults" class="btn-secondary">Reset Defaults</button>
        <button @click="saveSettings" :disabled="saving" class="btn-primary">
          <svg v-if="saving" class="btn-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" stroke-dasharray="31.4" stroke-dashoffset="10"></circle>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
            <polyline points="17 21 17 13 7 13 7 21"></polyline>
            <polyline points="7 3 7 8 15 8"></polyline>
          </svg>
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>

    <div v-if="saved" class="save-toast">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
      Settings saved successfully!
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading settings...</p>
    </div>

    <div v-else class="settings-content">
      <div class="settings-grid">
        <section class="settings-card">
          <div class="card-header">
            <div class="card-icon general">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
              </svg>
            </div>
            <h2 class="card-title">General</h2>
          </div>

          <div class="setting-item">
            <label class="setting-label">Language</label>
            <select v-model="general.language" class="setting-input">
              <option value="en">English</option>
              <option value="fa">فارسی (Persian)</option>
            </select>
          </div>

          <div class="setting-item">
            <label class="setting-label">Default Reminder Interval</label>
            <div class="input-with-unit">
              <input v-model.number="general.notification_interval_default" type="number" min="1" max="120" class="setting-input">
              <span class="unit">min</span>
            </div>
            <p class="setting-hint">How often to remind about unstarted planned work</p>
          </div>

          <div class="setting-item">
            <label class="setting-label">Session Poll Interval</label>
            <div class="input-with-unit">
              <input v-model.number="general.session_poll_interval" type="number" min="10" max="600" class="setting-input">
              <span class="unit">sec</span>
            </div>
            <p class="setting-hint">How often to check for session updates</p>
          </div>
        </section>

        <section class="settings-card">
          <div class="card-header">
            <div class="card-icon notifications">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
            </div>
            <h2 class="card-title">Notifications</h2>
          </div>

          <div
            v-for="type in notificationTypes"
            :key="type.key"
            class="notification-card"
          >
            <div class="notif-header">
              <div class="notif-info">
                <h3 class="notif-title">{{ type.label }}</h3>
                <p class="notif-desc">{{ type.description }}</p>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" v-model="notifications[type.key].enabled">
                <span class="toggle-slider"></span>
              </label>
            </div>

            <div v-if="notifications[type.key].enabled" class="notif-config">
              <label class="toggle-inline">
                <input type="checkbox" v-model="notifications[type.key].config.sound_enabled">
                <span class="toggle-label-text">Play sound</span>
              </label>

              <div v-if="notifications[type.key].config.sound_enabled" class="sound-config">
                <div class="sound-row">
                  <select v-model="notifications[type.key].config.sound_file" class="setting-input setting-sm">
                    <option v-for="sound in availableSounds" :key="sound" :value="sound">{{ sound }}</option>
                  </select>
                  <button @click="previewSound(notifications[type.key].config.sound_file)" class="btn-preview" title="Preview sound">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
                      <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                  </button>
                </div>
                <div class="sound-row">
                  <span class="sound-label">Play count</span>
                  <select v-model.number="notifications[type.key].config.sound_repeat" class="setting-input setting-sm">
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
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page { max-width: 1280px; margin: 0 auto; padding: 2rem; --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.page-title { font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.025em; }
.page-subtitle { color: #64748b; margin: 0.25rem 0 0; font-size: 0.95rem; }
.header-actions { display: flex; gap: 0.75rem; }

.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border: none; border-radius: 12px; font-size: 0.95rem; font-weight: 600; cursor: pointer; transition: all var(--transition); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { padding: 0.75rem 1.25rem; border: 1px solid #e2e8f0; background: white; border-radius: 12px; font-size: 0.9rem; font-weight: 500; color: #334155; cursor: pointer; transition: all var(--transition); }
.btn-secondary:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-spinner { width: 16px; height: 16px; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.save-toast { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1rem; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 10px; color: #059669; font-size: 0.875rem; font-weight: 500; margin-bottom: 1.5rem; animation: slideDown 0.3s ease; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

.loading-state { display: flex; flex-direction: column; align-items: center; padding: 4rem 2rem; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 3px solid #e2e8f0; border-top-color: #6366f1; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 1rem; }

.settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }

.settings-card { background: white; border-radius: 16px; border: 1px solid #e2e8f0; padding: 1.5rem; }
.card-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; }
.card-icon { display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 10px; }
.card-icon.general { background: #eef2ff; color: #6366f1; }
.card-icon.notifications { background: #fef3c7; color: #d97706; }
.card-title { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0; }

.setting-item { margin-bottom: 1.25rem; }
.setting-label { display: block; font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 0.5rem; }
.setting-input { width: 100%; padding: 0.625rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 0.9rem; color: #0f172a; background: white; transition: all var(--transition); }
.setting-input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
.setting-hint { font-size: 0.75rem; color: #94a3b8; margin: 0.375rem 0 0; }
.input-with-unit { display: flex; align-items: center; gap: 0.5rem; }
.input-with-unit .setting-input { flex: 1; }
.unit { font-size: 0.85rem; color: #64748b; flex-shrink: 0; }

.notification-card { padding: 1rem; background: #f8fafc; border-radius: 12px; margin-bottom: 0.75rem; }
.notif-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.notif-title { font-size: 0.9rem; font-weight: 600; color: #0f172a; margin: 0; }
.notif-desc { font-size: 0.8rem; color: #64748b; margin: 0.125rem 0 0; }

.toggle-switch { position: relative; flex-shrink: 0; }
.toggle-switch input { display: none; }
.toggle-slider { display: block; width: 40px; height: 22px; background: #cbd5e1; border-radius: 11px; position: relative; transition: all var(--transition); cursor: pointer; }
.toggle-slider::after { content: ''; position: absolute; width: 16px; height: 16px; background: white; border-radius: 50%; top: 3px; left: 3px; transition: all var(--transition); box-shadow: 0 1px 3px rgba(0,0,0,0.15); }
.toggle-switch input:checked + .toggle-slider { background: #6366f1; }
.toggle-switch input:checked + .toggle-slider::after { left: 21px; }

.notif-config { margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #e2e8f0; }
.toggle-inline { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; margin-bottom: 0.75rem; }
.toggle-inline input[type="checkbox"] { width: 16px; height: 16px; accent-color: #6366f1; cursor: pointer; }
.toggle-label-text { font-size: 0.85rem; color: #334155; }

.sound-config { display: flex; flex-direction: column; gap: 0.5rem; margin-left: 1.5rem; }
.sound-row { display: flex; align-items: center; gap: 0.5rem; }
.sound-label { font-size: 0.8rem; color: #64748b; min-width: 80px; }
.setting-sm { max-width: 200px; }
.btn-preview { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; border: 1px solid #e2e8f0; background: white; border-radius: 8px; cursor: pointer; color: #6366f1; transition: all var(--transition); flex-shrink: 0; }
.btn-preview:hover { background: #6366f1; color: white; border-color: #6366f1; }

@media (max-width: 768px) {
  .settings-page { padding: 1rem; }
  .page-header { flex-direction: column; gap: 1rem; }
  .settings-grid { grid-template-columns: 1fr; }
}
</style>
