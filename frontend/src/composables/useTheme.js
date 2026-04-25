import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'ub-theme'
const theme = ref('system')
const systemDark = ref(false)
let initialized = false

function apply() {
  const isDark = theme.value === 'dark' || (theme.value === 'system' && systemDark.value)
  document.documentElement.classList.toggle('dark', isDark)
}

function init() {
  if (initialized || typeof window === 'undefined') return
  initialized = true
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'light' || stored === 'dark' || stored === 'system') {
    theme.value = stored
  }
  if (window.matchMedia) {
    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    systemDark.value = mql.matches
    const onChange = (e) => { systemDark.value = e.matches }
    if (mql.addEventListener) mql.addEventListener('change', onChange)
    else mql.addListener(onChange)
  }
  watch([theme, systemDark], apply, { immediate: true })
}

const resolvedTheme = computed(() =>
  theme.value === 'system' ? (systemDark.value ? 'dark' : 'light') : theme.value
)

export function useTheme() {
  init()

  function setTheme(t) {
    theme.value = t
    try { localStorage.setItem(STORAGE_KEY, t) } catch {}
  }

  function cycleTheme() {
    const next = theme.value === 'light' ? 'dark' : theme.value === 'dark' ? 'system' : 'light'
    setTheme(next)
  }

  return { theme, resolvedTheme, setTheme, cycleTheme }
}
